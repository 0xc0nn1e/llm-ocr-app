"""Centralized error codes and their Japanese messages.

Each error has a stable machine-readable `code` (used by the frontend and
logs) and a human-facing Japanese `message`. Keeping them here avoids
scattering message strings across the codebase and prevents the same error
from being worded differently in two places.
"""

from enum import Enum


class ErrorCode(str, Enum):
    """Stable error codes returned to the client."""

    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    EMPTY_FILE = "EMPTY_FILE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    INVALID_RESPONSE = "INVALID_RESPONSE"


class AppError(Exception):

    code: ErrorCode
    http_status: int

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnsupportedFileType(AppError):
    code = ErrorCode.UNSUPPORTED_FILE_TYPE
    http_status = 400


class EmptyFile(AppError):
    code = ErrorCode.EMPTY_FILE
    http_status = 400


class FileTooLarge(AppError):
    code = ErrorCode.FILE_TOO_LARGE
    http_status = 400

class ProviderError(AppError):
    """The LLM provider call failed (network, API error, etc.)."""

    code = ErrorCode.PROVIDER_ERROR
    http_status = 502


class InvalidResponse(AppError):
    """The provider returned data that doesn't match the expected schema."""

    code = ErrorCode.INVALID_RESPONSE
    http_status = 502