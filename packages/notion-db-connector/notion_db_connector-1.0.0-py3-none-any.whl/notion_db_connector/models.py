# -*- coding: utf-8 -*-
"""Data models and data mapping logic for Notion objects."""

from datetime import date, datetime
from typing import Any, Dict


# A simplified representation of a Notion Page
NotionPage = Dict[str, Any]


class DataMapper:
    """Handles data conversion between Python native types and Notion API formats."""

    @staticmethod
    def python_to_notion_properties(data: Dict[str, Any], schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Converts a dictionary of Python native types to Notion's property format.
        If a schema is provided, it's used to correctly handle ambiguous types
        like strings (which could be rich_text, select, etc.).

        Args:
            data: A dictionary where keys are property names and values are
                  Python native types.
            schema: (Optional) The database schema to resolve ambiguous types.

        Returns:
            A dictionary formatted for the Notion API's 'properties' object.
        """
        properties = {}
        schema = schema or {}

        for name, value in data.items():
            if value is None:
                continue

            prop_type = None
            prop_value = None
            prop_schema = schema.get(name, {})

            if isinstance(value, bool):
                prop_type = "checkbox"
                prop_value = value
            elif isinstance(value, (int, float)):
                prop_type = "number"
                prop_value = value
            elif isinstance(value, (date, datetime)):
                prop_type = "date"
                prop_value = {"start": value.isoformat()}
            elif isinstance(value, str):
                # Use schema to differentiate between string-based types
                schema_type = prop_schema.get("type")
                if schema_type == "select":
                    prop_type = "select"
                    prop_value = {"name": value}
                elif schema_type == "title":
                    prop_type = "title"
                    prop_value = [{"type": "text", "text": {"content": value}}]
                else: # Default to rich_text
                    prop_type = "rich_text"
                    prop_value = [{"type": "text", "text": {"content": value}}]

            if prop_type:
                properties[name] = {prop_type: prop_value}

        return properties

    @staticmethod
    def notion_to_python_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts a Notion API 'properties' object to a simple Python dictionary.

        Args:
            properties: A dictionary in the Notion API 'properties' format.

        Returns:
            A dictionary with property names and simplified Python native values.
        """
        py_properties = {}
        for name, prop_data in properties.items():
            prop_type = prop_data.get("type")
            value = None

            if prop_type == "title":
                if prop_data.get("title"):
                    value = prop_data["title"][0].get("text", {}).get("content")
            elif prop_type == "rich_text":
                if prop_data.get("rich_text"):
                    value = prop_data["rich_text"][0].get("text", {}).get("content")
            elif prop_type == "number":
                value = prop_data.get("number")
            elif prop_type == "checkbox":
                value = prop_data.get("checkbox")
            elif prop_type == "date":
                if prop_data.get("date"):
                    value = prop_data["date"].get("start")
            elif prop_type == "select":
                if prop_data.get("select"):
                    value = prop_data["select"].get("name")
            elif prop_type in ("last_edited_time", "created_time"):
                value = prop_data.get(prop_type)

            py_properties[name] = value

        return py_properties

    @staticmethod
    def extract_page_data(page: NotionPage) -> Dict[str, Any]:
        """
        Extracts key information and simplified properties from a Notion page object.

        Args:
            page: A Notion page object from the API.

        Returns:
            A dictionary containing the page ID and its simplified properties.
        """
        if not page:
            return {}

        # Start with the simplified properties
        data = DataMapper.notion_to_python_properties(page.get("properties", {}))

        # Then, add metadata. This ensures the page's true 'id' overwrites
        # any property that might also be named 'id'.
        data["archived"] = page.get("archived", False)
        data["id"] = page.get("id")

        return data
