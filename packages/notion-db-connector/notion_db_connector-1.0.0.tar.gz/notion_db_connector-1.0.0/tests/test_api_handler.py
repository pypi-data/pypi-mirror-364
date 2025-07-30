# -*- coding: utf-8 -*-
"""Unit tests for the async ApiHandler."""
import asyncio
import pytest
from unittest.mock import AsyncMock
from notion_client.errors import APIResponseError

from notion_db_connector.api_handler import ApiHandler
from notion_db_connector.exceptions import APIError, ObjectNotFoundError, RateLimitError

@pytest.fixture
def mock_notion_client(mocker):
    """Fixture to mock the notion_client.AsyncClient."""
    mock = mocker.patch("notion_client.AsyncClient").return_value
    mock.databases.query = AsyncMock()
    mock.pages.update = AsyncMock()
    return mock

def run_async(coro):
    """Helper function to run an async test."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)

def test_query_database_success(mock_notion_client):
    """Test successful database query with pagination."""
    async def main():
        mock_notion_client.databases.query.side_effect = [
            {"results": [{"id": "page1"}], "has_more": True, "next_cursor": "cursor1"},
            {"results": [{"id": "page2"}], "has_more": False, "next_cursor": None},
        ]
        handler = ApiHandler(api_key="fake-key")
        result = await handler.query_database("db1")
        
        assert result == [{"id": "page1"}, {"id": "page2"}]
        assert mock_notion_client.databases.query.call_count == 2
    run_async(main())

def test_query_database_not_found(mock_notion_client):
    """Tests that ObjectNotFoundError is raised for a non-existent database."""
    async def main():
        api_error = APIResponseError(response=AsyncMock(), message="", code="object_not_found")
        mock_notion_client.databases.query.side_effect = api_error
        handler = ApiHandler(api_key="fake-key")
        with pytest.raises(ObjectNotFoundError, match="Database with ID 'db1' not found."):
            await handler.query_database(database_id="db1")
    run_async(main())

def test_query_database_rate_limited_raises_exception(mock_notion_client):
    """Tests that RateLimitError is raised when the rate limit is hit."""
    async def main():
        api_error = APIResponseError(response=AsyncMock(), message="", code="rate_limited")
        mock_notion_client.databases.query.side_effect = api_error
        handler = ApiHandler(api_key="fake-key")
        with pytest.raises(RateLimitError):
            await handler.query_database(database_id="db1")
    run_async(main())

def test_update_page_generic_api_error(mock_notion_client):
    """Tests that a generic APIError is raised for other API failures."""
    async def main():
        api_error = APIResponseError(response=AsyncMock(), message="Server error.", code="internal_server_error")
        mock_notion_client.pages.update.side_effect = api_error
        handler = ApiHandler(api_key="fake-key")
        # Match the actual error message format from the ApiHandler
        with pytest.raises(APIError, match="Failed to update page:"):
            await handler.update_page(page_id="page1", properties={})
    run_async(main())
