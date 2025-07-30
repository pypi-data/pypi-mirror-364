# -*- coding: utf-8 -*-
"""High-level client for interacting with Notion databases."""
import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from cachetools import TTLCache
from dotenv import load_dotenv

from .api_handler import ApiHandler
from .exceptions import APIError, ConfigurationError, ObjectNotFoundError, SQLTranslationError
from .models import DataMapper
from .query_translator import QueryTranslator
from .sql_parser import parse_sql


class NotionDBClient:
    """
    The main client for interacting with Notion databases.

    This class provides both a synchronous and asynchronous, Pythonic interface
    for performing CRUD operations and executing SQL queries.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        db_name_to_id_map: Optional[Dict[str, str]] = None,
        caching: bool = False,
        cache_ttl: int = 300,
    ):
        """
        Initializes the client.

        The API key can be provided directly or loaded from a .env file
        by setting the `NOTION_API_KEY` environment variable.

        Args:
            api_key: The Notion API integration token. If not provided, it will be
                     loaded from the `NOTION_API_KEY` environment variable.
            timeout: The timeout for API requests in seconds.
            db_name_to_id_map: A dictionary mapping SQL table names to
                               Notion Database IDs.
            caching: If True, query results will be cached in memory.
            cache_ttl: Time-to-live for cached items in seconds.
        
        Raises:
            ConfigurationError: If the API key is not provided and cannot be
                                found in the environment variables.
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("NOTION_API_KEY")
            if not api_key:
                raise ConfigurationError(
                    "No API key provided. Please pass the `api_key` argument or "
                    "set the `NOTION_API_KEY` environment variable in a .env file."
                )

        assert isinstance(db_name_to_id_map, dict) or db_name_to_id_map is None, \
            "db_name_to_id_map must be a dictionary or None."

        self._api_handler = ApiHandler(api_key=api_key, timeout=timeout)
        self._mapper = DataMapper()
        self.db_name_to_id_map = db_name_to_id_map or {}
        self.db_schemas = {} # Maps DB ID to its schema
        
        # Eagerly fetch schemas for all initially mapped databases.
        # Since __init__ cannot be async, we run the async method synchronously.
        if self.db_name_to_id_map:
            asyncio.run(self._populate_initial_schemas())

        # The translator is now stateless
        self._query_translator = QueryTranslator()

        self.caching = caching
        if self.caching:
            self.cache = TTLCache(maxsize=1024, ttl=cache_ttl)
        else:
            self.cache = None

        self.local_store = {}  # Stores database_id -> pandas DataFrame

    async def _populate_initial_schemas(self):
        """Asynchronously fetches schemas for all initially mapped databases."""
        tasks = [self.async_get_database_schema(db_id) for db_id in self.db_name_to_id_map.values()]
        await asyncio.gather(*tasks)

    def execute_sql(self, sql_string: str) -> Any:
        """Synchronously executes a raw SQL query."""
        return asyncio.run(self.async_execute_sql(sql_string))

    async def async_execute_sql(self, sql_string: str) -> Any:
        """
        Parses, translates, and asynchronously executes a raw SQL query.

        Args:
            sql_string: The raw SQL query to execute.

        Returns:
            The result of the operation, which could be a list of pages
            for SELECT, or a status dictionary for other operations.
        """
        expression = parse_sql(sql_string)
        translated_query = self._query_translator.translate(
            expression,
            db_name_to_id_map=self.db_name_to_id_map,
            db_schemas=self.db_schemas
        )

        operation = translated_query.pop("operation")

        if operation == "local_join":
            from .local_engine import execute_local_join
            
            left_db_id = translated_query.get("left_database_id")
            right_db_id = translated_query.get("right_database_id")

            if left_db_id not in self.local_store:
                raise ConfigurationError(f"左表 '{left_db_id}' 未在本地同步。请在执行 JOIN 前调用 `sync_to_local('{left_db_id}')`。")
            if right_db_id not in self.local_store:
                raise ConfigurationError(f"右表 '{right_db_id}' 未在本地同步。请在执行 JOIN 前调用 `sync_to_local('{right_db_id}')`。")

            left_df = self.local_store[left_db_id]
            right_df = self.local_store[right_db_id]

            return execute_local_join(left_df, right_df, translated_query)

        is_aggregate = translated_query.pop("is_aggregate", False)

        if is_aggregate:
            db_id = translated_query.get("database_id")
            if db_id not in self.local_store:
                raise ConfigurationError(
                    f"Database '{db_id}' not found in local store. "
                    f"Please call `sync_to_local('{db_id}')` before running an aggregate query."
                )
            
            from .local_engine import execute_local_query
            df = self.local_store[db_id]
            
            # The result from local_engine is already a DataFrame
            return execute_local_query(df, translated_query)

        if operation == "query":
            db_id = translated_query.get("database_id")
            filter_obj = translated_query.get("filter")
            sorts_obj = translated_query.get("sorts")

            pages = []
            if filter_obj and "page_id" in filter_obj:
                page_id = filter_obj["page_id"]
                try:
                    raw_page = await self._api_handler.retrieve_page(page_id)
                    pages = [self._mapper.extract_page_data(raw_page)]
                except ObjectNotFoundError:
                    pages = []
            else:
                pages = await self.async_query_database(
                    database_id=db_id, filter_obj=filter_obj, sorts_obj=sorts_obj
                )
            
            if translated_query.get("properties"):
                props_to_keep = translated_query["properties"]
                return [
                    {k: v for k, v in page.items() if k in props_to_keep or k == 'id'}
                    for page in pages
                ]
            return pages

        elif operation == "create_page":
            db_id = translated_query.pop("database_id")
            props = translated_query.pop("properties")
            return await self.async_create_page(database_id=db_id, data=props)

        elif operation == "update_pages":
            filter_obj = translated_query.get("filter")
            props_to_update = translated_query.pop("properties")

            pages_to_update = []
            if filter_obj and "page_id" in filter_obj:
                pages_to_update = [{"id": filter_obj["page_id"]}]
            else:
                db_id = translated_query.pop("database_id")
                pages_to_update = await self.async_query_database(database_id=db_id, filter_obj=filter_obj)

            update_tasks = [self.async_update_page(page['id'], props_to_update) for page in pages_to_update]
            updated_results = await asyncio.gather(*update_tasks)
            
            return {"updated_count": len(updated_results), "updated_pages": updated_results}

        elif operation == "delete_pages":
            filter_obj = translated_query.get("filter")
            
            pages_to_delete = []
            if filter_obj and "page_id" in filter_obj:
                pages_to_delete = [{"id": filter_obj["page_id"]}]
            else:
                db_id = translated_query.pop("database_id")
                pages_to_delete = await self.async_query_database(database_id=db_id, filter_obj=filter_obj)

            delete_tasks = [self.async_delete_page(page['id']) for page in pages_to_delete]
            await asyncio.gather(*delete_tasks)

            return {"deleted_count": len(pages_to_delete)}

        else:
            raise SQLTranslationError(f"Unsupported operation: {operation}")

    def _get_cache_key(self, *args, **kwargs) -> str:
        """Creates a stable cache key from arguments."""
        # Using json.dumps with sort_keys=True ensures that the same
        # dictionary with different key order produces the same key.
        return json.dumps((args, kwargs), sort_keys=True)

    def query_database(
        self,
        database_id: str,
        filter_obj: Optional[Dict[str, Any]] = None,
        sorts_obj: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Synchronously queries a database."""
        return asyncio.run(self.async_query_database(database_id, filter_obj, sorts_obj))

    async def async_query_database(
        self,
        database_id: str,
        filter_obj: Optional[Dict[str, Any]] = None,
        sorts_obj: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Asynchronously queries a database and returns a list of pages."""
        if self.caching:
            cache_key = self._get_cache_key(database_id=database_id, filter_obj=filter_obj, sorts_obj=sorts_obj)
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        raw_pages = await self._api_handler.query_database(
            database_id=database_id, filter_obj=filter_obj, sorts_obj=sorts_obj
        )
        
        result = [self._mapper.extract_page_data(page) for page in raw_pages]
        
        if self.caching:
            self.cache[cache_key] = result
            
        return result

    def create_page(self, database_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronously creates a new page in a database."""
        return asyncio.run(self.async_create_page(database_id, data))

    async def async_create_page(self, database_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Asynchronously creates a new page in a database."""
        try:
            schema = await self.async_get_database_schema(database_id)
            properties = self._mapper.python_to_notion_properties(data, schema)
            raw_page = await self._api_handler.create_page(
                database_id=database_id, properties=properties
            )
            return self._mapper.extract_page_data(raw_page)
        except ObjectNotFoundError:
            raise APIError(f"Failed to create page because database with ID '{database_id}' was not found.")

    def update_page(self, page_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronously updates an existing page's properties."""
        return asyncio.run(self.async_update_page(page_id, data))

    async def async_update_page(self, page_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Asynchronously updates an existing page's properties."""
        page_info = await self._api_handler.retrieve_page(page_id)
        database_id = page_info.get("parent", {}).get("database_id")
        if not database_id:
            raise APIError(f"Could not determine database for page ID '{page_id}'.")

        schema = await self.async_get_database_schema(database_id)
        properties = self._mapper.python_to_notion_properties(data, schema)
        
        raw_page = await self._api_handler.update_page(page_id=page_id, properties=properties)
        
        return self._mapper.extract_page_data(raw_page)

    def delete_page(self, page_id: str) -> Dict[str, Any]:
        """Synchronously deletes (archives) a page."""
        return asyncio.run(self.async_delete_page(page_id))

    async def async_delete_page(self, page_id: str) -> Dict[str, Any]:
        """Asynchronously deletes (archives) a page."""
        raw_page = await self._api_handler.archive_page(page_id=page_id)
        return self._mapper.extract_page_data(raw_page)

    def get_database_schema(self, database_id: str) -> Dict[str, Any]:
        """Synchronously retrieves the schema of a specific database."""
        return asyncio.run(self.async_get_database_schema(database_id))

    async def async_get_database_schema(self, database_id: str) -> Dict[str, Any]:
        """Asynchronously retrieves the schema of a specific database, using a cache."""
        if database_id in self.db_schemas:
            return self.db_schemas[database_id]

        database_info = await self._api_handler.retrieve_database(database_id)
        schema = database_info.get("properties", {})
        self.db_schemas[database_id] = schema
        return schema

    def create_database(self, parent_page_id: str, title: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronously creates a new Notion database."""
        return asyncio.run(self.async_create_database(parent_page_id, title, schema))

    async def async_create_database(self, parent_page_id: str, title: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Asynchronously creates a new Notion database."""
        full_payload = {
            "parent": {"page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "properties": schema
        }
        return await self._api_handler.create_database(payload=full_payload)

    def delete_database(self, database_id: str) -> Dict[str, Any]:
        """Synchronously deletes (archives) a Notion database."""
        return asyncio.run(self.async_delete_database(database_id))

    async def async_delete_database(self, database_id: str) -> Dict[str, Any]:
        """Asynchronously deletes (archives) a Notion database."""
        return await self._api_handler.delete_database(database_id=database_id)

    def update_database_schema(self, database_id: str, new_properties: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronously updates the schema of an existing database."""
        return asyncio.run(self.async_update_database_schema(database_id, new_properties))

    async def async_update_database_schema(self, database_id: str, new_properties: Dict[str, Any]) -> Dict[str, Any]:
        """Asynchronously updates the schema of an existing database."""
        return await self._api_handler.update_database_schema(
            database_id=database_id, new_properties=new_properties
        )

    def sync_to_local(self, database_id: str):
        """
        Synchronously fetches all pages from a Notion database and stores them
        locally as a pandas DataFrame.

        Args:
            database_id: The ID of the database to sync.
        """
        return asyncio.run(self.async_sync_to_local(database_id))

    async def async_sync_to_local(self, database_id: str):
        """
        Asynchronously fetches all pages from a Notion database and stores them
        locally as a pandas DataFrame.

        Args:
            database_id: The ID of the database to sync.
        """
        import pandas as pd

        all_raw_pages = await self._api_handler.query_database(database_id=database_id)
        
        processed_pages = [self._mapper.extract_page_data(page) for page in all_raw_pages]
        
        if not processed_pages:
            df = pd.DataFrame()
        else:
            df = pd.DataFrame(processed_pages)
            # Ensure 'id' column is always present, even if empty
            if 'id' not in df.columns:
                df['id'] = None
        
        self.local_store[database_id] = df
        
        # Eagerly cache the schema if it's not already there
        await self.async_get_database_schema(database_id)
