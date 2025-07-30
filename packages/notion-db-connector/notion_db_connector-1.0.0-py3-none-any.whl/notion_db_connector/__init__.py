# -*- coding: utf-8 -*-
"""A Python module to interact with Notion databases using a DB-like interface."""

from .client import NotionDBClient
from .exceptions import (
    APIError,
    ConfigurationError,
    NotionDBConnectorError,
    ObjectNotFoundError,
    RateLimitError,
    SQLParsingError,
    SQLTranslationError,
    UnsupportedOperationError,
)

__all__ = [
    "NotionDBClient",
    "NotionDBConnectorError",
    "ConfigurationError",
    "APIError",
    "RateLimitError",
    "ObjectNotFoundError",
    "SQLParsingError",
    "SQLTranslationError",
    "UnsupportedOperationError",
]