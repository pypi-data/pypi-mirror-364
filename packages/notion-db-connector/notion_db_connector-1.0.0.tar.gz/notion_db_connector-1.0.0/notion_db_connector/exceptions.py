# -*- coding: utf-8 -*-
"""Defines custom exceptions for the notion-db-connector module."""


class NotionDBConnectorError(Exception):
    """Base exception for all errors raised by this library."""
    pass


class ConfigurationError(NotionDBConnectorError):
    """Raised when there is a configuration problem."""
    pass


class APIError(NotionDBConnectorError):
    """Raised when the Notion API returns an error."""
    pass


class RateLimitError(APIError):
    """Raised when the Notion API rate limit is exceeded."""
    pass


class ObjectNotFoundError(APIError):
    """Raised when a requested Notion object (e.g., database, page) is not found."""
    pass


class SQLParsingError(NotionDBConnectorError):
    """Raised for errors during SQL parsing."""
    pass


class UnsupportedOperationError(NotionDBConnectorError):
    """Raised when an unsupported SQL operation is attempted."""
    pass


class SQLTranslationError(NotionDBConnectorError):
    """Raised for errors during the translation of SQL to Notion API calls."""
    pass
