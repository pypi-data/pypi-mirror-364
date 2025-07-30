# -*- coding: utf-8 -*-
"""Tests for productization enhancements like error handling and caching."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from notion_client.errors import APIResponseError

from notion_db_connector.api_handler import ApiHandler
from notion_db_connector.client import NotionDBClient
from notion_db_connector.exceptions import RateLimitError

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)

@pytest.fixture
def mock_notion_client_instance(mocker):
    """Fixture to mock the notion_client.AsyncClient instance."""
    return mocker.patch("notion_client.AsyncClient").return_value

def test_rate_limit_retry(mocker, mock_notion_client_instance):
    """Verify that the client retries upon receiving a rate limit error."""
    async def main():
        # The first call raises rate limit, the second is a mock of the successful response
        mock_notion_client_instance.databases.query.side_effect = [
            APIResponseError(response=AsyncMock(), code="rate_limited", message=""),
            AsyncMock(return_value={"results": [{"id": "page1"}], "has_more": False})()
        ]
        mock_sleep = mocker.patch("asyncio.sleep", return_value=None)
        handler = ApiHandler(api_key="fake-key")
        # We need to manually set the client for the handler in this test
        handler.client = mock_notion_client_instance
        result = await handler.query_database(database_id="db1")
        assert mock_notion_client_instance.databases.query.call_count == 2
        assert mock_sleep.call_count == 1
        assert result == [{"id": "page1"}]
    run_async(main())

def test_rate_limit_fail_after_retries(mocker, mock_notion_client_instance):
    """Verify that the client gives up after exhausting all retries."""
    async def main():
        mock_notion_client_instance.databases.query.side_effect = APIResponseError(
            response=MagicMock(), code="rate_limited", message=""
        )
        mock_sleep = mocker.patch("asyncio.sleep", return_value=None)
        handler = ApiHandler(api_key="fake-key")
        with pytest.raises(RateLimitError):
            await handler.query_database(database_id="db1")
        assert mock_notion_client_instance.databases.query.call_count == 5
        assert mock_sleep.call_count == 4
    run_async(main())

@pytest.fixture
def mock_api_handler(mocker):
    """Fixture to mock the ApiHandler."""
    mock_handler = MagicMock(spec=ApiHandler)
    mock_handler.query_database = AsyncMock()
    mocker.patch("notion_db_connector.client.ApiHandler", return_value=mock_handler)
    return mock_handler

@pytest.fixture
def mock_asyncio_run(mocker):
    return mocker.patch("asyncio.run")

def test_caching_logic(mock_api_handler, mock_asyncio_run):
    """Verify that caching works as expected: hit, miss, and TTL expiration."""
    async def main():
        raw_api_response = [{"object": "page", "id": "page1", "properties": {"Name": {"id": "title", "type": "title", "title": [{"type": "text", "text": {"content": "Test"}}]}}}]
        mock_api_handler.query_database.return_value = raw_api_response
        client = NotionDBClient(api_key="fake-key", caching=True, cache_ttl=1)

        result1 = await client.async_query_database(database_id="db1")
        assert mock_api_handler.query_database.call_count == 1
        assert result1[0]["Name"] == "Test"

        result2 = await client.async_query_database(database_id="db1")
        assert mock_api_handler.query_database.call_count == 1
        assert result2 == result1

        await asyncio.sleep(1.5)

        result3 = await client.async_query_database(database_id="db1")
        assert mock_api_handler.query_database.call_count == 2
        assert result3 == result1
    run_async(main())

def test_caching_disabled(mock_api_handler, mock_asyncio_run):
    """Verify that no caching occurs when the feature is disabled."""
    async def main():
        mock_api_handler.query_database.return_value = [{"id": "page1"}]
        client = NotionDBClient(api_key="fake-key", caching=False)
        await client.async_query_database(database_id="db1")
        await client.async_query_database(database_id="db1")
        assert mock_api_handler.query_database.call_count == 2
    run_async(main())
