# -*- coding: utf-8 -*-
"""Handles direct interactions with the Notion API via the notion-client SDK."""
import asyncio
import logging
import random
from functools import wraps

import notion_client
from notion_client.errors import APIResponseError

from .exceptions import APIError, ConfigurationError, ObjectNotFoundError, RateLimitError

logger = logging.getLogger(__name__)


def _retry_on_rate_limit(max_retries=5, base_delay=1.0):
    """
    An async decorator to handle Notion's rate limit errors with exponential backoff and jitter.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt == max_retries - 1:
                        logger.error("Max retries reached for rate-limited request. Aborting.")
                        raise e
                    
                    backoff_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        "Rate limit exceeded. Retrying in %.2f seconds... (Attempt %d/%d)",
                        backoff_time,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(backoff_time)
            # This part should not be reachable, but as a fallback
            raise RateLimitError("Exhausted all retries for rate-limited request.")
        return wrapper
    return decorator


class ApiHandler:
    """A low-level async wrapper for the notion-client SDK."""

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initializes the ApiHandler.

        Args:
            api_key: The Notion API integration token.
            timeout: The timeout for API requests in seconds.

        Raises:
            ConfigurationError: If the API key is not provided.
        """
        if not api_key:
            raise ConfigurationError("Notion API key is required.")

        self.client = notion_client.AsyncClient(auth=api_key, timeout_ms=timeout * 1000)

    @_retry_on_rate_limit()
    async def query_database(
        self, database_id: str, filter_obj: dict = None, sorts_obj: list = None
    ) -> list:
        """
        Queries a Notion database, handling pagination to retrieve all results.

        Args:
            database_id: The ID of the database to query.
            filter_obj: The Notion API filter object.
            sorts_obj: The Notion API sorts object.

        Returns:
            A list of all page objects found in the query.

        Raises:
            ObjectNotFoundError: If the database with the given ID does not exist.
            RateLimitError: If the API rate limit is exceeded after retries.
            APIError: For other generic API errors.
        """
        results = []
        next_cursor = None
        
        while True:
            try:
                # Dynamically build query parameters to avoid sending `null` for optional fields
                query_params = {
                    "database_id": database_id,
                    "start_cursor": next_cursor,
                }
                if filter_obj:
                    query_params["filter"] = filter_obj
                if sorts_obj:
                    query_params["sorts"] = sorts_obj

                response = await self.client.databases.query(**query_params)
                results.extend(response.get("results", []))
                if response.get("has_more"):
                    next_cursor = response.get("next_cursor")
                else:
                    break
            except APIResponseError as e:
                if e.code == "object_not_found":
                    raise ObjectNotFoundError(f"Database with ID '{database_id}' not found.") from e
                if e.code == "rate_limited":
                    # This will be caught by the decorator
                    raise RateLimitError("Notion API rate limit exceeded.") from e
                raise APIError(f"Notion API error: {e}") from e
        return results

    @_retry_on_rate_limit()
    async def retrieve_database(self, database_id: str) -> dict:
        """
        Retrieves metadata for a specific database.

        Args:
            database_id: The ID of the database to retrieve.

        Returns:
            The database object.
        """
        try:
            return await self.client.databases.retrieve(database_id=database_id)
        except APIResponseError as e:
            # Notion returns a generic error for page IDs used in database endpoints.
            # We'll treat this as a "not found" error for simplicity.
            if e.code == "object_not_found" or "is a page, not a database" in str(e):
                raise ObjectNotFoundError(f"Database with ID '{database_id}' not found or is a page.") from e
            if e.code == "rate_limited":
                raise RateLimitError("Notion API rate limit exceeded.") from e
            raise APIError(f"Failed to retrieve database: {e}") from e

    @_retry_on_rate_limit()
    async def create_page(self, database_id: str, properties: dict) -> dict:
        """
        Creates a new page in a database.

        Args:
            database_id: The ID of the parent database.
            properties: The properties of the new page, in Notion API format.

        Returns:
            The newly created page object.
        """
        try:
            return await self.client.pages.create(parent={"database_id": database_id}, properties=properties)
        except APIResponseError as e:
            if e.code == "rate_limited":
                raise RateLimitError("Notion API rate limit exceeded.") from e
            raise APIError(f"Failed to create page: {e}") from e

    @_retry_on_rate_limit()
    async def update_page(self, page_id: str, properties: dict) -> dict:
        """
        Updates the properties of an existing page.

        Args:
            page_id: The ID of the page to update.
            properties: The properties to update, in Notion API format.

        Returns:
            The updated page object.
        """
        try:
            return await self.client.pages.update(page_id=page_id, properties=properties)
        except APIResponseError as e:
            if e.code == "object_not_found":
                raise ObjectNotFoundError(f"Page with ID '{page_id}' not found.") from e
            if e.code == "rate_limited":
                raise RateLimitError("Notion API rate limit exceeded.") from e
            raise APIError(f"Failed to update page: {e}") from e

    @_retry_on_rate_limit()
    async def retrieve_page(self, page_id: str) -> dict:
        """
        Retrieves a single page object.

        Args:
            page_id: The ID of the page to retrieve.

        Returns:
            The page object.
        """
        try:
            return await self.client.pages.retrieve(page_id=page_id)
        except APIResponseError as e:
            if e.code == "object_not_found":
                raise ObjectNotFoundError(f"Page with ID '{page_id}' not found.") from e
            if e.code == "rate_limited":
                raise RateLimitError("Notion API rate limit exceeded.") from e
            raise APIError(f"Failed to retrieve page: {e}") from e

    @_retry_on_rate_limit()
    async def archive_page(self, page_id: str) -> dict:
        """
        Archives a page (soft delete).

        Args:
            page_id: The ID of the page to archive.

        Returns:
            The archived page object.
        """
        try:
            return await self.client.pages.update(page_id=page_id, archived=True)
        except APIResponseError as e:
            if e.code == "object_not_found":
                raise ObjectNotFoundError(f"Page with ID '{page_id}' not found.") from e
            if e.code == "rate_limited":
                raise RateLimitError("Notion API rate limit exceeded.") from e
            raise APIError(f"Failed to archive page: {e}") from e

    @_retry_on_rate_limit()
    async def create_database(self, payload: dict) -> dict:
        """
        Creates a new database using the provided payload.

        Args:
            payload: The full payload for the Notion API's databases.create endpoint.
                     This should include 'parent', 'title', and 'properties'.

        Returns:
            The newly created database object.
        """
        try:
            return await self.client.databases.create(**payload)
        except APIResponseError as e:
            if e.code == "rate_limited":
                raise RateLimitError("Notion API rate limit exceeded.") from e
            # A validation error can occur if the schema is malformed or parent_id is wrong
            if e.code == "validation_error":
                raise APIError(f"Failed to create database due to a validation error. Check payload. Details: {e}") from e
            raise APIError(f"Failed to create database: {e}") from e

    @_retry_on_rate_limit()
    async def delete_database(self, database_id: str) -> dict:
        """
        Deletes (archives) a database.

        Args:
            database_id: The ID of the database to archive.

        Returns:
            The archived database object.
        """
        try:
            # Notion "deletes" databases by archiving them.
            return await self.client.databases.update(database_id=database_id, archived=True)
        except APIResponseError as e:
            if e.code == "object_not_found":
                raise ObjectNotFoundError(f"Database with ID '{database_id}' not found.") from e
            if e.code == "rate_limited":
                raise RateLimitError("Notion API rate limit exceeded.") from e
            raise APIError(f"Failed to delete (archive) database: {e}") from e

    @_retry_on_rate_limit()
    async def update_database_schema(self, database_id: str, new_properties: dict) -> dict:
        """
        Updates the schema of an existing database.

        Args:
            database_id: The ID of the database to update.
            new_properties: The new properties to set for the database.

        Returns:
            The updated database object.
        """
        try:
            return await self.client.databases.update(database_id=database_id, properties=new_properties)
        except APIResponseError as e:
            if e.code == "object_not_found":
                raise ObjectNotFoundError(f"Database with ID '{database_id}' not found.") from e
            if e.code == "rate_limited":
                raise RateLimitError("Notion API rate limit exceeded.") from e
            if e.code == "validation_error":
                 raise APIError(f"Failed to update database schema due to a validation error. Check the new properties. Details: {e}") from e
            raise APIError(f"Failed to update database schema: {e}") from e
