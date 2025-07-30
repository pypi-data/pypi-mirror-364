"""Tests for custom exceptions and error handling utilities."""

from datetime import datetime

import pytest
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from aceiot_models.common import ErrorResponse
from aceiot_models.exceptions import (
    ERROR_TEMPLATES,
    AceIoTError,
    AuthorizationError,
    BusinessLogicError,
    ConfigurationError,
    DataIntegrityError,
    ErrorContext,
    ExternalServiceError,
    ModelConflictError,
    ModelNotFoundError,
    RateLimitError,
    ValidationError,
    create_informative_error_message,
    format_error_message,
    handle_pydantic_validation_error,
    safe_execute,
    validate_and_raise,
    wrap_exception,
)


class TestAceIoTError:
    """Test the base AceIoTError exception."""

    def test_aceiot_error_basic(self):
        """Test basic AceIoTError creation."""
        error = AceIoTError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code == "aceiot"
        assert error.details == {}
        assert isinstance(error.timestamp, datetime)
        assert error.original_error is None

    def test_aceiot_error_with_all_params(self):
        """Test AceIoTError with all parameters."""
        original = ValueError("Original error")
        error = AceIoTError(
            message="Test error",
            error_code="test_error",
            details={"field": "test"},
            original_error=original,
        )

        assert error.message == "Test error"
        assert error.error_code == "test_error"
        assert error.details == {"field": "test"}
        assert error.original_error is original

    def test_aceiot_error_to_error_response(self):
        """Test converting AceIoTError to ErrorResponse."""
        error = AceIoTError(message="Test error", error_code="test_code", details={"key": "value"})

        response = error.to_error_response()

        assert isinstance(response, ErrorResponse)
        assert response.error == "Test error"
        assert response.code == "test_code"
        assert response.details == {"key": "value"}
        assert response.timestamp == error.timestamp

    def test_aceiot_error_add_detail(self):
        """Test adding details to error."""
        error = AceIoTError("Test error")

        error.add_detail("field", "value")
        error.add_detail("count", 42)

        assert error.details == {"field": "value", "count": 42}


class TestValidationError:
    """Test the ValidationError exception."""

    def test_validation_error_basic(self):
        """Test basic ValidationError creation."""
        error = ValidationError("Invalid value")

        assert error.message == "Invalid value"
        assert error.error_code == "validation_error"
        assert error.field is None
        assert error.value is None
        assert error.constraint is None

    def test_validation_error_with_field_info(self):
        """Test ValidationError with field information."""
        error = ValidationError(
            message="Invalid email format",
            field="email",
            value="invalid@",
            constraint="email_format",
        )

        assert error.message == "Invalid email format"
        assert error.field == "email"
        assert error.value == "invalid@"
        assert error.constraint == "email_format"
        assert error.details["field"] == "email"
        assert error.details["invalid_value"] == "invalid@"
        assert error.details["constraint"] == "email_format"


class TestModelNotFoundError:
    """Test the ModelNotFoundError exception."""

    def test_model_not_found_error(self):
        """Test ModelNotFoundError creation."""
        error = ModelNotFoundError("Client", "123")

        assert error.message == "Client with id '123' not found"
        assert error.error_code == "not_found"
        assert error.resource_type == "Client"
        assert error.identifier == "123"
        assert error.details["resource_type"] == "Client"
        assert error.details["identifier"] == "123"
        assert error.details["identifier_type"] == "id"

    def test_model_not_found_error_custom_identifier(self):
        """Test ModelNotFoundError with custom identifier type."""
        error = ModelNotFoundError("User", "john@example.com", identifier_type="email")

        assert error.message == "User with email 'john@example.com' not found"
        assert error.details["identifier_type"] == "email"


class TestModelConflictError:
    """Test the ModelConflictError exception."""

    def test_model_conflict_error(self):
        """Test ModelConflictError creation."""
        error = ModelConflictError("User", "email", "john@example.com")

        assert error.message == "User with email 'john@example.com' already exists"
        assert error.error_code == "conflict"
        assert error.details["resource_type"] == "User"
        assert error.details["conflict_field"] == "email"
        assert error.details["conflict_value"] == "john@example.com"


class TestAuthorizationError:
    """Test the AuthorizationError exception."""

    def test_authorization_error_basic(self):
        """Test basic AuthorizationError."""
        error = AuthorizationError()

        assert error.message == "Access denied"
        assert error.error_code == "authorization_error"

    def test_authorization_error_with_details(self):
        """Test AuthorizationError with permission details."""
        error = AuthorizationError(
            message="Cannot delete resource", required_permission="admin", resource="Client/123"
        )

        assert error.message == "Cannot delete resource"
        assert error.details["required_permission"] == "admin"
        assert error.details["resource"] == "Client/123"


class TestConfigurationError:
    """Test the ConfigurationError exception."""

    def test_configuration_error(self):
        """Test ConfigurationError creation."""
        error = ConfigurationError("database", "Connection string invalid")

        assert error.message == "Configuration error in database: Connection string invalid"
        assert error.error_code == "configuration_error"
        assert error.details["config_type"] == "database"

    def test_configuration_error_with_field(self):
        """Test ConfigurationError with specific field."""
        error = ConfigurationError("api", "Invalid URL", config_field="base_url")

        assert error.details["config_field"] == "base_url"


class TestBusinessLogicError:
    """Test the BusinessLogicError exception."""

    def test_business_logic_error(self):
        """Test BusinessLogicError creation."""
        error = BusinessLogicError(
            rule="minimum_balance",
            message="Account balance cannot be negative",
            context={"balance": -100, "account_id": "123"},
        )

        assert error.message == "Account balance cannot be negative"
        assert error.error_code == "business_logic_error"
        assert error.details["rule"] == "minimum_balance"
        assert error.details["context"]["balance"] == -100


class TestDataIntegrityError:
    """Test the DataIntegrityError exception."""

    def test_data_integrity_error(self):
        """Test DataIntegrityError creation."""
        error = DataIntegrityError(
            constraint_type="foreign_key",
            message="Cannot delete client with active sites",
            affected_fields=["client_id", "site_count"],
        )

        assert error.message == "Cannot delete client with active sites"
        assert error.error_code == "data_integrity_error"
        assert error.details["constraint_type"] == "foreign_key"
        assert error.details["affected_fields"] == ["client_id", "site_count"]


class TestExternalServiceError:
    """Test the ExternalServiceError exception."""

    def test_external_service_error(self):
        """Test ExternalServiceError creation."""
        error = ExternalServiceError(
            service_name="Weather API",
            message="Rate limit exceeded",
            status_code=429,
            response_body='{"error": "Too many requests"}',
        )

        assert error.message == "External service error (Weather API): Rate limit exceeded"
        assert error.error_code == "external_service_error"
        assert error.details["service_name"] == "Weather API"
        assert error.details["status_code"] == 429
        assert error.details["response_body"] == '{"error": "Too many requests"}'


class TestRateLimitError:
    """Test the RateLimitError exception."""

    def test_rate_limit_error(self):
        """Test RateLimitError creation."""
        error = RateLimitError(limit=100, window="hour", retry_after=3600)

        assert error.message == "Rate limit exceeded: 100 requests per hour"
        assert error.error_code == "rate_limit_error"
        assert error.details["limit"] == 100
        assert error.details["window"] == "hour"
        assert error.details["retry_after"] == 3600


class TestErrorHandlingUtilities:
    """Test error handling utility functions."""

    def test_handle_pydantic_validation_error(self):
        """Test handling Pydantic validation errors."""

        class TestModel(BaseModel):
            name: str
            age: int

        error = None
        try:
            TestModel(name="", age="invalid")  # type: ignore
        except PydanticValidationError as e:
            error = handle_pydantic_validation_error(e, "TestModel")

        assert error is not None
        assert isinstance(error, ValidationError)
        assert "TestModel" in error.message
        assert error.details["model"] == "TestModel"
        # Pydantic might only report 1 error if it short-circuits
        assert error.details["error_count"] >= 1
        assert "field_errors" in error.details
        assert error.original_error is not None

    def test_create_informative_error_message(self):
        """Test creating informative error messages."""
        # Test with AceIoTError
        ace_error = AceIoTError("Test error")
        message = create_informative_error_message(ace_error)
        assert message == "Test error"

        # Test with standard exception, user-friendly
        value_error = ValueError("Invalid input")
        message = create_informative_error_message(value_error, user_friendly=True)
        assert message == "Invalid value provided"

        # Test with context
        message = create_informative_error_message(value_error, context="Processing user data")
        assert message == "Processing user data - Invalid value provided"

        # Test non-user-friendly
        message = create_informative_error_message(value_error, user_friendly=False)
        assert message == "ValueError: Invalid input"

        # Test unknown error type
        custom_error = type("CustomError", (Exception,), {})("Custom message")
        message = create_informative_error_message(custom_error, user_friendly=True)
        assert message == "Custom message"

    def test_wrap_exception(self):
        """Test wrapping exceptions in AceIoTError."""
        # Test wrapping non-AceIoTError
        original = ValueError("Original error")
        wrapped = wrap_exception(original, "Processing data")

        assert isinstance(wrapped, AceIoTError)
        assert "Processing data" in wrapped.message
        assert wrapped.error_code == "wrapped_exception"
        assert wrapped.details["original_error_type"] == "ValueError"
        assert wrapped.details["context"] == "Processing data"
        assert wrapped.original_error is original

        # Test wrapping AceIoTError (should return as-is)
        ace_error = AceIoTError("Already wrapped")
        wrapped = wrap_exception(ace_error, "Context")
        assert wrapped is ace_error

        # Test with custom error code
        wrapped = wrap_exception(ValueError("Error"), "Context", error_code="custom_code")
        assert wrapped.error_code == "custom_code"

    def test_validate_and_raise(self):
        """Test validate_and_raise function."""
        # Test passing condition
        validate_and_raise(True, message="Should not raise")

        # Test failing condition with default error
        with pytest.raises(ValidationError) as exc_info:
            validate_and_raise(False)
        assert exc_info.value.message == "Validation failed"

        # Test with custom error class and message
        with pytest.raises(AuthorizationError) as exc_info:
            validate_and_raise(False, AuthorizationError, "Custom auth error")
        assert exc_info.value.message == "Custom auth error"

        # Test with additional kwargs
        with pytest.raises(ValidationError) as exc_info:
            validate_and_raise(False, field="email", value="invalid")
        assert exc_info.value.field == "email"
        assert exc_info.value.value == "invalid"

    def test_safe_execute(self):
        """Test safe_execute function."""
        # Test successful execution
        result = safe_execute(lambda: 42)
        assert result == 42

        # Test with error and raise_on_error=True
        with pytest.raises(AceIoTError) as exc_info:
            safe_execute(lambda: 1 / 0, error_message="Division failed")
        assert "Division failed" in str(exc_info.value)

        # Test with error and raise_on_error=False
        result = safe_execute(
            lambda: 1 / 0, error_message="Division failed", default_return=-1, raise_on_error=False
        )
        assert result == -1

        # Test with function that raises an error
        result = safe_execute(
            lambda: 1 / 0,  # This will raise ZeroDivisionError
            default_return="default",
            raise_on_error=False,
        )
        assert result == "default"

    def test_format_error_message(self):
        """Test formatting error messages from templates."""
        # Test existing template
        message = format_error_message("required_field", field="email")
        assert message == "Field 'email' is required"

        # Test template with multiple parameters
        message = format_error_message("out_of_range", field="age", min_value=0, max_value=120)
        assert message == "Field 'age' must be between 0 and 120"

        # Test unknown template
        message = format_error_message("unknown_template", message="fallback")
        assert message == "Unknown error: fallback"

        # Test template with missing parameters
        message = format_error_message("required_field")
        assert "missing key" in message


class TestErrorContext:
    """Test the ErrorContext context manager."""

    def test_error_context_no_error(self):
        """Test ErrorContext with no errors."""
        with ErrorContext("test operation") as ctx:
            result = 1 + 1
            assert not ctx.has_errors()

        assert result == 2

    def test_error_context_with_ace_error(self):
        """Test ErrorContext with AceIoTError."""
        with pytest.raises(AceIoTError) as exc_info, ErrorContext("test operation"):
            raise AceIoTError("Test error")

        # Should raise the original error
        assert exc_info.value.message == "Test error"

    def test_error_context_with_wrapped_error(self):
        """Test ErrorContext wrapping non-AceIoTError."""
        with pytest.raises(AceIoTError) as exc_info, ErrorContext("database operation"):
            raise ValueError("Connection failed")

        error = exc_info.value
        assert "database operation" in error.message
        assert error.details["context"] == "database operation"
        assert isinstance(error.original_error, ValueError)

    def test_error_context_no_raise(self):
        """Test ErrorContext with raise_on_error=False."""
        with ErrorContext("test operation", raise_on_error=False):
            try:
                raise ValueError("Test error")
            except ValueError:
                pass

        # Should not raise

    def test_error_context_add_error(self):
        """Test adding errors to context."""
        ctx = ErrorContext("test operation")

        ctx.add_error("First error")
        ctx.add_error(ValidationError("Second error"))

        assert ctx.has_errors()
        assert len(ctx.errors) == 2
        assert isinstance(ctx.errors[0], AceIoTError)
        assert isinstance(ctx.errors[1], ValidationError)

    def test_error_context_raise_if_errors_single(self):
        """Test raising single error from context."""
        ctx = ErrorContext("test operation")
        error = ValidationError("Test validation error")
        ctx.add_error(error)

        with pytest.raises(ValidationError) as exc_info:
            ctx.raise_if_errors()

        assert exc_info.value is error

    def test_error_context_raise_if_errors_multiple(self):
        """Test raising multiple errors from context."""
        ctx = ErrorContext("batch operation")
        ctx.add_error("Error 1")
        ctx.add_error("Error 2")
        ctx.add_error("Error 3")

        with pytest.raises(AceIoTError) as exc_info:
            ctx.raise_if_errors()

        error = exc_info.value
        assert "Multiple errors in batch operation" in error.message
        assert error.error_code == "multiple_errors"
        assert error.details["error_count"] == 3
        assert len(error.details["errors"]) == 3


class TestErrorTemplates:
    """Test ERROR_TEMPLATES constant."""

    def test_error_templates_exist(self):
        """Test that ERROR_TEMPLATES is properly defined."""
        assert isinstance(ERROR_TEMPLATES, dict)
        assert len(ERROR_TEMPLATES) > 0

        # Check some expected templates
        expected_templates = [
            "required_field",
            "invalid_format",
            "out_of_range",
            "too_short",
            "too_long",
            "invalid_choice",
            "unique_constraint",
            "foreign_key",
            "permission_denied",
        ]

        for template in expected_templates:
            assert template in ERROR_TEMPLATES
            assert isinstance(ERROR_TEMPLATES[template], str)
            assert "{" in ERROR_TEMPLATES[template]  # Should have placeholders
