"""Comprehensive error handling and exceptions for ACE IoT models."""

import traceback
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from .common import ErrorResponse


class AceIoTError(Exception):
    """Base exception class for ACE IoT models."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.lower().replace("error", "")
        self.details = details or {}
        self.original_error = original_error
        self.timestamp = datetime.now(UTC)

    def to_error_response(self) -> ErrorResponse:
        """Convert exception to ErrorResponse model."""
        return ErrorResponse(
            error=self.message, code=self.error_code, details=self.details, timestamp=self.timestamp
        )

    def add_detail(self, key: str, value: Any) -> "AceIoTError":
        """Add detail to the error."""
        self.details[key] = value
        return self


class ValidationError(AceIoTError):
    """Exception for validation errors."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None,
        constraint: str | None = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["invalid_value"] = str(value)
        if constraint:
            details["constraint"] = constraint

        super().__init__(
            message=message,
            error_code="validation_error",
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )
        self.field = field
        self.value = value
        self.constraint = constraint


class ModelNotFoundError(AceIoTError):
    """Exception for when a requested model is not found."""

    def __init__(self, resource_type: str, identifier: str, identifier_type: str = "id", **kwargs):
        message = f"{resource_type} with {identifier_type} '{identifier}' not found"
        details = {
            "resource_type": resource_type,
            "identifier": identifier,
            "identifier_type": identifier_type,
        }

        super().__init__(message=message, error_code="not_found", details=details, **kwargs)
        self.resource_type = resource_type
        self.identifier = identifier


class ModelConflictError(AceIoTError):
    """Exception for when a model operation conflicts with existing data."""

    def __init__(self, resource_type: str, conflict_field: str, conflict_value: str, **kwargs):
        message = f"{resource_type} with {conflict_field} '{conflict_value}' already exists"
        details = {
            "resource_type": resource_type,
            "conflict_field": conflict_field,
            "conflict_value": conflict_value,
        }

        super().__init__(message=message, error_code="conflict", details=details, **kwargs)


class AuthorizationError(AceIoTError):
    """Exception for authorization/permission errors."""

    def __init__(
        self,
        message: str = "Access denied",
        required_permission: str | None = None,
        resource: str | None = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if required_permission:
            details["required_permission"] = required_permission
        if resource:
            details["resource"] = resource

        super().__init__(
            message=message, error_code="authorization_error", details=details, **kwargs
        )


class ConfigurationError(AceIoTError):
    """Exception for configuration-related errors."""

    def __init__(self, config_type: str, message: str, config_field: str | None = None, **kwargs):
        details = {"config_type": config_type}
        if config_field:
            details["config_field"] = config_field

        super().__init__(
            message=f"Configuration error in {config_type}: {message}",
            error_code="configuration_error",
            details=details,
            **kwargs,
        )


class BusinessLogicError(AceIoTError):
    """Exception for business logic violations."""

    def __init__(self, rule: str, message: str, context: dict[str, Any] | None = None, **kwargs):
        details: dict[str, Any] = {"rule": rule}
        if context:
            details["context"] = context

        super().__init__(
            message=message, error_code="business_logic_error", details=details, **kwargs
        )


class DataIntegrityError(AceIoTError):
    """Exception for data integrity violations."""

    def __init__(
        self, constraint_type: str, message: str, affected_fields: list[str] | None = None, **kwargs
    ):
        details: dict[str, Any] = {"constraint_type": constraint_type}
        if affected_fields:
            details["affected_fields"] = affected_fields

        super().__init__(
            message=message, error_code="data_integrity_error", details=details, **kwargs
        )


class ExternalServiceError(AceIoTError):
    """Exception for external service communication errors."""

    def __init__(
        self,
        service_name: str,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        **kwargs,
    ):
        details: dict[str, Any] = {"service_name": service_name}
        if status_code:
            details["status_code"] = status_code
        if response_body:
            details["response_body"] = response_body

        super().__init__(
            message=f"External service error ({service_name}): {message}",
            error_code="external_service_error",
            details=details,
            **kwargs,
        )


class RateLimitError(AceIoTError):
    """Exception for rate limiting errors."""

    def __init__(self, limit: int, window: str, retry_after: int | None = None, **kwargs):
        message = f"Rate limit exceeded: {limit} requests per {window}"
        details = {"limit": limit, "window": window}
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(message=message, error_code="rate_limit_error", details=details, **kwargs)


# Utility functions for error handling
def handle_pydantic_validation_error(
    error: PydanticValidationError, model_name: str
) -> ValidationError:
    """Convert Pydantic ValidationError to our custom ValidationError."""
    error_messages = []
    field_errors = {}

    for pydantic_error in error.errors():
        field_path = ".".join(str(loc) for loc in pydantic_error["loc"])
        error_msg = pydantic_error["msg"]
        error_type = pydantic_error["type"]
        input_value = pydantic_error.get("input")

        error_messages.append(f"{field_path}: {error_msg}")
        field_errors[field_path] = {"message": error_msg, "type": error_type, "input": input_value}

    return ValidationError(
        message=f"Validation failed for {model_name}: {'; '.join(error_messages)}",
        details={
            "model": model_name,
            "field_errors": field_errors,
            "error_count": len(error.errors()),
        },
        original_error=error,
    )


def create_informative_error_message(
    error: Exception, context: str | None = None, user_friendly: bool = True
) -> str:
    """Create an informative error message from any exception."""
    if isinstance(error, AceIoTError):
        return error.message

    error_type = type(error).__name__
    error_message = str(error)

    if user_friendly:
        # Map common error types to user-friendly messages
        friendly_messages = {
            "ValueError": "Invalid value provided",
            "TypeError": "Incorrect data type",
            "KeyError": "Required field missing",
            "AttributeError": "Invalid field or operation",
            "ConnectionError": "Connection failed",
            "TimeoutError": "Operation timed out",
        }

        base_message = friendly_messages.get(error_type, error_message)
    else:
        base_message = f"{error_type}: {error_message}"

    if context:
        return f"{context} - {base_message}"

    return base_message


def wrap_exception(error: Exception, context: str, error_code: str | None = None) -> AceIoTError:
    """Wrap any exception in an AceIoTError with context."""
    if isinstance(error, AceIoTError):
        return error

    return AceIoTError(
        message=create_informative_error_message(error, context),
        error_code=error_code or "wrapped_exception",
        details={
            "original_error_type": type(error).__name__,
            "original_error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
        },
        original_error=error,
    )


def validate_and_raise(
    condition: bool,
    error_class: type = ValidationError,
    message: str = "Validation failed",
    **kwargs,
) -> None:
    """Validate condition and raise error if False."""
    if not condition:
        raise error_class(message, **kwargs)


def safe_execute(
    func: Callable[[], Any],
    error_message: str = "Operation failed",
    default_return: Any = None,
    raise_on_error: bool = True,
) -> Any:
    """Safely execute a function with error handling."""
    try:
        return func()
    except Exception as e:
        if raise_on_error:
            raise wrap_exception(e, error_message) from e
        else:
            return default_return


# Error message templates
ERROR_TEMPLATES = {
    "required_field": "Field '{field}' is required",
    "invalid_format": "Field '{field}' has invalid format: {format_requirement}",
    "out_of_range": "Field '{field}' must be between {min_value} and {max_value}",
    "too_short": "Field '{field}' must be at least {min_length} characters long",
    "too_long": "Field '{field}' cannot exceed {max_length} characters",
    "invalid_choice": "Field '{field}' must be one of: {valid_choices}",
    "unique_constraint": "Field '{field}' must be unique, '{value}' already exists",
    "foreign_key": "Referenced {resource_type} with {field}='{value}' not found",
    "circular_reference": "Circular reference detected in {field}",
    "permission_denied": "Permission denied: {required_permission} required for {resource}",
    "resource_locked": "{resource_type} '{identifier}' is locked and cannot be modified",
    "dependency_exists": "Cannot delete {resource_type} '{identifier}', dependencies exist: {dependencies}",
    "invalid_state": "{resource_type} '{identifier}' is in invalid state for operation: {operation}",
}


def format_error_message(template_key: str, **kwargs) -> str:
    """Format error message using template."""
    template = ERROR_TEMPLATES.get(template_key, "Unknown error: {message}")
    try:
        return template.format(**kwargs)
    except KeyError as e:
        return f"Error formatting error message template '{template_key}': missing key {e}"


# Context managers for error handling
class ErrorContext:
    """Context manager for handling errors within a specific context."""

    def __init__(self, context: str, raise_on_error: bool = True):
        self.context = context
        self.raise_on_error = raise_on_error
        self.errors = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val and self.raise_on_error and not isinstance(exc_val, AceIoTError):
            # Wrap non-AceIoTError exceptions
            wrapped_error = wrap_exception(exc_val, self.context)
            raise wrapped_error from exc_val
        return False

    def add_error(self, error: Exception | str):
        """Add an error to the context."""
        if isinstance(error, str):
            error = AceIoTError(error)
        self.errors.append(error)

    def has_errors(self) -> bool:
        """Check if context has any errors."""
        return len(self.errors) > 0

    def raise_if_errors(self):
        """Raise exception if there are any errors."""
        if self.errors:
            if len(self.errors) == 1:
                raise self.errors[0]
            else:
                error_messages = [str(e) for e in self.errors]
                raise AceIoTError(
                    message=f"Multiple errors in {self.context}: {'; '.join(error_messages)}",
                    error_code="multiple_errors",
                    details={
                        "context": self.context,
                        "error_count": len(self.errors),
                        "errors": error_messages,
                    },
                )


# Export all exceptions and utilities
__all__ = [
    "ERROR_TEMPLATES",
    "AceIoTError",
    "AuthorizationError",
    "BusinessLogicError",
    "ConfigurationError",
    "DataIntegrityError",
    "ErrorContext",
    "ExternalServiceError",
    "ModelConflictError",
    "ModelNotFoundError",
    "RateLimitError",
    "ValidationError",
    "create_informative_error_message",
    "format_error_message",
    "handle_pydantic_validation_error",
    "safe_execute",
    "validate_and_raise",
    "wrap_exception",
]
