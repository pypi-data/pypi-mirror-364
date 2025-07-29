# paritydeals_sdk/models/__init__.py
"""
Pydantic Models for the ParityDeals SDK.

This package contains Pydantic models used for data validation,
serialization, and deserialization for API requests and responses.
"""

# Import models from submodules to make them accessible
# directly from paritydeals_sdk.models
# e.g., from paritydeals_sdk.models import ReportUsagePayload

from .reporting import (
    BaseResponse,
    ReportUsagePayload,
    ReportUsageResponse,
    ReportEventPayload,
    ReportEventResponse,
    # ReportEventPayloadWithDatetime # If you decide to use and export this
)

__all__ = [
    "BaseResponse",
    "ReportUsagePayload",
    "ReportUsageResponse",
    "ReportEventPayload",
    "ReportEventResponse",
    # "ReportEventPayloadWithDatetime",
]
