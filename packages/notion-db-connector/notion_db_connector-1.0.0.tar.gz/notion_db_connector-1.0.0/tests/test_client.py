# -*- coding: utf-8 -*-
"""Unit tests for the NotionDBClient, covering both sync and async interfaces."""
import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from notion_db_connector.client import NotionDBClient
from notion_db_connector.exceptions import ConfigurationError

MOCK_PAGE_LIST = [{"id": "page1", "properties": {"Name": {"type": "title", "title": [{"text": {"content": "Test Page"}}]}}}]
MOCK_EXTRACTED_PAGE = {"id": "page1", "Name": "Test Page"}
MOCK_SCHEMA = {"Name": {"title": {}}}

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)

@pytest.fixture
def mock_api_handler(mocker):
    handler_instance = MagicMock()
    handler_instance.retrieve_database = AsyncMock(return_value={"properties": MOCK_SCHEMA})
    handler_instance.query_database = AsyncMock(return_value=MOCK_PAGE_LIST)
    handler_instance.create_page = AsyncMock(return_value=MOCK_PAGE_LIST[0])
    mocker.patch("notion_db_connector.client.ApiHandler", return_value=handler_instance)
    return handler_instance

@pytest.fixture
def mock_mapper(mocker):
    mapper_instance = MagicMock()
    mapper_instance.extract_page_data.return_value = MOCK_EXTRACTED_PAGE
    mocker.patch("notion_db_connector.client.DataMapper", return_value=mapper_instance)
    return mapper_instance

@pytest.fixture
def mock_asyncio_run(mocker):
    """Mocks asyncio.run to prevent issues during client initialization in tests."""
    return mocker.patch("asyncio.run")

def test_async_query_database(mock_api_handler, mock_mapper, mock_asyncio_run):
    async def main():
        client = NotionDBClient(api_key="fake_key")
        results = await client.async_query_database(database_id="db1")
        mock_api_handler.query_database.assert_called_once_with(database_id="db1", filter_obj=None, sorts_obj=None)
        assert len(results) == 1
        assert results[0]["id"] == "page1"
    run_async(main())

def test_sync_query_database_wrapper(mocker, mock_asyncio_run):
    mocker.patch("notion_db_connector.client.ApiHandler")
    mocker.patch("notion_db_connector.client.DataMapper")
    mock_async_method = mocker.patch.object(NotionDBClient, 'async_query_database', new_callable=AsyncMock)
    client = NotionDBClient(api_key="fake_key")
    client.query_database(database_id="db1", filter_obj={"prop": "val"})
    # The sync wrapper calls the async method with positional arguments.
    # The assertion must match this call signature.
    mock_async_method.assert_called_once_with("db1", {"prop": "val"}, None)

@patch('os.getenv', return_value='env_key')
@patch('notion_db_connector.client.ApiHandler')
@patch('asyncio.run')
def test_client_initialization_from_env(mock_run, mock_api_handler_class, mock_getenv):
    NotionDBClient()
    mock_api_handler_class.assert_called_once_with(api_key='env_key', timeout=30)

def test_client_initialization_failure_no_key(mocker):
    mocker.patch('os.getenv', return_value=None)
    with pytest.raises(ConfigurationError, match="No API key provided"):
        NotionDBClient()

def test_async_create_page(mock_api_handler, mock_mapper, mock_asyncio_run):
    async def main():
        client = NotionDBClient(api_key="fake_key")
        page_data = {"Name": "Test Page"}
        result = await client.async_create_page(database_id="db1", data=page_data)
        mock_api_handler.create_page.assert_called_once()
        assert result["id"] == "page1"
    run_async(main())

def test_sync_create_page_wrapper(mocker, mock_asyncio_run):
    mocker.patch("notion_db_connector.client.ApiHandler")
    mocker.patch("notion_db_connector.client.DataMapper")
    client = NotionDBClient(api_key="fake_key")
    client.create_page(database_id="db1", data={"Name": "Test"})
    mock_asyncio_run.assert_called_once()
    called_coro = mock_asyncio_run.call_args[0][0]
    assert called_coro.cr_frame.f_code.co_name == "async_create_page"
