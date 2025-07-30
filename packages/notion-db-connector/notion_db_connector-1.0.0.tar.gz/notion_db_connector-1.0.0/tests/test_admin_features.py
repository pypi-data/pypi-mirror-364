# -*- coding: utf-8 -*-
"""Unit tests for the administrative features of the NotionDBClient."""

import pytest
from unittest.mock import AsyncMock
from notion_db_connector.client import NotionDBClient

API_KEY = "test_api_key"

@pytest.fixture
def mock_api_handler(mocker):
    """Fixture to mock the ApiHandler."""
    mock = mocker.patch('notion_db_connector.client.ApiHandler', autospec=True)
    mock_instance = mock.return_value
    # Ensure all relevant methods are async mocks
    mock_instance.create_database = AsyncMock()
    mock_instance.delete_database = AsyncMock()
    mock_instance.update_database_schema = AsyncMock()
    return mock_instance

@pytest.fixture
def client(mock_api_handler):
    """Fixture to create a NotionDBClient with a mocked ApiHandler."""
    return NotionDBClient(api_key=API_KEY, db_name_to_id_map={"test_db": "db_id"})

import asyncio

def test_create_database_with_new_loop(client, mock_api_handler):
    """
    Tests async_create_database by creating and managing a new event loop for the test.
    """
    parent_page_id = "parent_page_123"
    title = "Test Database"
    schema = {"Name": {"title": {}}}
    expected_return_value = {"id": "new_db_123"}
    
    mock_api_handler.create_database.return_value = expected_return_value

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            client.async_create_database(parent_page_id=parent_page_id, title=title, schema=schema)
        )
    finally:
        loop.close()
        asyncio.set_event_loop(None)

    expected_payload = {
        "parent": {"page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": schema
    }
    
    mock_api_handler.create_database.assert_called_once_with(payload=expected_payload)
    assert result == expected_return_value

def test_delete_database_with_new_loop(client, mock_api_handler):
    """Tests async_delete_database with a manually managed event loop."""
    database_id_to_delete = "db_to_delete_456"
    expected_return_value = {"id": database_id_to_delete, "archived": True}
    mock_api_handler.delete_database.return_value = expected_return_value

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(client.async_delete_database(database_id=database_id_to_delete))
    finally:
        loop.close()
        asyncio.set_event_loop(None)

    mock_api_handler.delete_database.assert_called_once_with(database_id=database_id_to_delete)
    assert result == expected_return_value

def test_update_database_schema_with_new_loop(client, mock_api_handler):
    """Tests async_update_database_schema with a manually managed event loop."""
    database_id_to_update = "db_to_update_789"
    new_schema = {"Status": {"status": {}}}
    expected_return_value = {"id": database_id_to_update, "properties": new_schema}
    mock_api_handler.update_database_schema.return_value = expected_return_value

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            client.async_update_database_schema(database_id=database_id_to_update, new_properties=new_schema)
        )
    finally:
        loop.close()
        asyncio.set_event_loop(None)

    mock_api_handler.update_database_schema.assert_called_once_with(
        database_id=database_id_to_update, new_properties=new_schema
    )
    assert result == expected_return_value
