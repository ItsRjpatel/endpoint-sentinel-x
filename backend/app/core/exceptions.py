from typing import Any


class SentinelException(Exception):
    """Base exception for Endpoint Sentinel X."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class EntityNotFoundException(SentinelException):
    """Exception raised when a requested resource is not found."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, code="NOT_FOUND", details=details)


class AuthenticationException(SentinelException):
    """Exception raised for authentication failure."""

    def __init__(
        self,
        message: str = "Could not validate credentials",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, code="UNAUTHORIZED", details=details)


class ForbiddenException(SentinelException):
    """Exception raised when user does not have permission."""

    def __init__(self, message: str = "Permission denied", details: dict[str, Any] | None = None):
        super().__init__(message, code="FORBIDDEN", details=details)


class ValidationException(SentinelException):
    """Exception raised when data validation fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)
