# paritydeals_sdk/__init__.py
"""
ParityDeals Python SDK

A Python SDK for interacting with the ParityDeals API to report usage and events.
Supports both synchronous and asynchronous operations using a single client class,
instantiated via static factory methods `ParityDeals.create_sync_client` or
`ParityDeals.create_async_client`.
"""

__version__ = "1.0.1"

# Import constants to be available at the package level
import logging
from .constants import BEHAVIOUR_CHOICES

logger = logging.getLogger(__name__)  # Using __name__ will make it 'paritydeals_sdk'
if not logger.handlers:  # Add handler only if no handlers are already configured
    logger.addHandler(logging.NullHandler())

# Import exceptions to be available at the package level
from .exceptions import (
    APIError,
    AuthenticationError,
    InvalidRequestError,
    ServerError,
    NotFoundError
)

# Import the unified client class
from .client import ParityDeals

__all__ = [
    # Logger (optional to export, but can be useful for users to configure)
    "logger",

    # Constants
    "BEHAVIOUR_CHOICES",

    # Exceptions
    "APIError",
    "AuthenticationError",
    "InvalidRequestError",
    "ServerError",
    "NotFoundError",

    # Client Class (factories are part of this class)
    "ParityDeals",

    # Version
    "__version__",
]
