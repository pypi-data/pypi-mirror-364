# -*- coding: utf-8 -*-
"""
@author: 乔肃
@file: test_sql_interface.py
@time: 2025/07/24
@description: Unit tests for the async SQL interface layer.
"""
import asyncio
import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock, call, patch

from notion_db_connector import NotionDBClient
from notion_db_connector.exceptions import SQLParsingError, SQLTranslationError, ConfigurationError

DB_ID = "db-1234"
DB_NAME = "my_test_db"
DB_MAP = {DB_NAME: DB_ID}
MOCK_SCHEMA = {"Name": {"type": "title"}, "Status": {"type": "select"}, "Value": {"type": "number"}}

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)

@pytest.fixture
def mock_client(mocker):
    mocker.patch("asyncio.run")
    client = NotionDBClient(api_key="fake-key", db_name_to_id_map=DB_MAP)
    client._api_handler = MagicMock()
    client._api_handler.query_database = AsyncMock(return_value=[])
    client._api_handler.create_page = AsyncMock(return_value={})
    client._api_handler.update_page = AsyncMock(return_value={})
    client._api_handler.archive_page = AsyncMock(return_value={})
    client._api_handler.retrieve_page = AsyncMock(return_value={})
    client._mapper = MagicMock()
    client._mapper.python_to_notion_properties = MagicMock(return_value={"mocked": "props"})
    client._mapper.extract_page_data = MagicMock(side_effect=lambda p: {"id": p.get("id", "default_id")})
    client.db_schemas[DB_ID] = MOCK_SCHEMA
    return client

def test_select_with_where(mock_client):
    async def main():
        sql = f"SELECT Name FROM {DB_NAME} WHERE Status = 'Done'"
        await mock_client.async_execute_sql(sql)
        expected_filter = {"property": "Status", "select": {"equals": "Done"}}
        mock_client._api_handler.query_database.assert_called_once_with(database_id=DB_ID, filter_obj=expected_filter, sorts_obj=None)
    run_async(main())

def test_insert_query(mock_client):
    async def main():
        sql = f"INSERT INTO {DB_NAME} (Name, Value) VALUES ('New Task', 123)"
        await mock_client.async_execute_sql(sql)
        mock_client._api_handler.create_page.assert_called_once()
    run_async(main())

def test_update_query(mock_client):
    async def main():
        # The query returns a page that the mapper will process
        raw_page = {"id": "page-to-update", "properties": {}}
        mock_client._api_handler.query_database.return_value = [raw_page]

        # When updating, the client first retrieves the page to get the parent db_id
        mock_client._api_handler.retrieve_page.return_value = {"id": "page-to-update", "parent": {"database_id": DB_ID}}
        
        # The mapper will extract the id
        mock_client._mapper.extract_page_data.return_value = {"id": "page-to-update"}

        sql = f"UPDATE {DB_NAME} SET Status = 'Done' WHERE Name = 'My Task'"
        await mock_client.async_execute_sql(sql)
        
        expected_filter = {"property": "Name", "title": {"equals": "My Task"}}
        mock_client._api_handler.query_database.assert_called_once_with(database_id=DB_ID, filter_obj=expected_filter, sorts_obj=None)
        
        # Check that update_page is called with the correct page_id and properties
        mock_client._api_handler.update_page.assert_called_once()
        call_args = mock_client._api_handler.update_page.call_args
        assert call_args.kwargs['page_id'] == 'page-to-update'
        assert 'properties' in call_args.kwargs
    run_async(main())

def test_delete_query_concurrently(mock_client):
    async def main():
        mock_client._api_handler.query_database.return_value = [{"id": "page-1"}, {"id": "page-2"}]
        sql = f"DELETE FROM {DB_NAME} WHERE Status = 'Archived'"
        result = await mock_client.async_execute_sql(sql)
        assert mock_client._api_handler.archive_page.call_count == 2
        mock_client._api_handler.archive_page.assert_has_calls([call(page_id="page-1"), call(page_id="page-2")], any_order=True)
        assert result['deleted_count'] == 2
    run_async(main())

def test_invalid_sql_syntax(mock_client):
    async def main():
        with pytest.raises(SQLParsingError):
            await mock_client.async_execute_sql("SELECT * FRM my_test_db")
    run_async(main())

def test_unsupported_operation(mock_client):
    async def main():
        with pytest.raises(SQLTranslationError):
            await mock_client.async_execute_sql("SELECT * FROM table1 JOIN table2 ON table1.id = table2.id")
    run_async(main())

def test_local_query_success_integration(mock_client):
    """An integration-style test for the local query engine."""
    async def main():
        sample_data = pd.DataFrame({
            'Status': ['Done', 'Done', 'In Progress', 'Done'],
            'Value': [10, 20, 5, 15],
            'id': ['p1', 'p2', 'p3', 'p4']
        })
        mock_client.local_store[DB_ID] = sample_data
        sql = f"SELECT Status, COUNT(*) as count, SUM(Value) as total FROM {DB_NAME} GROUP BY Status ORDER BY Status"
        
        # No patch, use the real local engine
        result_df = await mock_client.async_execute_sql(sql)
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 2
        assert list(result_df.columns) == ['Status', 'count', 'total']
        
        # Check 'Done' group
        done_group = result_df[result_df['Status'] == 'Done']
        assert done_group.iloc[0]['count'] == 3
        assert done_group.iloc[0]['total'] == 45
        
        # Check 'In Progress' group
        progress_group = result_df[result_df['Status'] == 'In Progress']
        assert progress_group.iloc[0]['count'] == 1
        assert progress_group.iloc[0]['total'] == 5

    run_async(main())

def test_local_query_db_not_synced(mock_client):
    async def main():
        if DB_ID in mock_client.local_store:
            del mock_client.local_store[DB_ID]
        sql = f"SELECT Status, COUNT(*) FROM {DB_NAME} GROUP BY Status"
        with pytest.raises(ConfigurationError, match=f"Database '{DB_ID}' not found in local store."):
            await mock_client.async_execute_sql(sql)
    run_async(main())
