"""Tests for common models and utilities."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from aceiot_models.common import (
    VALID_PER_PAGE_VALUES,
    AuthToken,
    BaseEntityModel,
    BaseModel,
    BaseUUIDEntityModel,
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    create_generic_error,
    create_not_found_error,
    create_validation_error,
    validate_per_page,
)


class TestBaseModel:
    """Test the BaseModel configuration."""

    def test_base_model_creation(self):
        """Test that BaseModel can be instantiated."""

        # Create a simple model for testing
        class TestModel(BaseModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)
        assert model.name == "test"
        assert model.value == 42

    def test_base_model_from_attributes(self):
        """Test that BaseModel supports from_attributes."""

        class TestModel(BaseModel):
            name: str
            value: int

        # Mock an object with attributes
        class MockObject:
            name = "test"
            value = 42

        obj = MockObject()
        model = TestModel.model_validate(obj)
        assert model.name == "test"
        assert model.value == 42

    def test_base_model_json_serialization(self):
        """Test JSON serialization with datetime."""

        class TestModel(BaseModel):
            name: str
            timestamp: datetime

        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)
        model = TestModel(name="test", timestamp=dt)

        json_str = model.model_dump_json()
        assert "2024-01-15T10:30:45+00:00" in json_str or "2024-01-15T10:30:45Z" in json_str


class TestPaginatedResponse:
    """Test the PaginatedResponse model."""

    def test_paginated_response_creation(self, sample_paginated_response):
        """Test creating a paginated response."""
        response = PaginatedResponse[dict](
            page=1, pages=5, per_page=10, total=47, items=[{"id": 1}, {"id": 2}]
        )

        assert response.page == 1
        assert response.pages == 5
        assert response.per_page == 10
        assert response.total == 47
        assert len(response.items) == 2

    def test_paginated_response_validation_positive_integers(self):
        """Test validation of positive integer fields."""
        with pytest.raises(PydanticValidationError) as exc_info:
            PaginatedResponse[dict](page=-1, pages=5, per_page=10, total=47, items=[])

        errors = exc_info.value.errors()
        assert any("non-negative" in error["msg"].lower() for error in errors)

    def test_paginated_response_empty_items(self):
        """Test paginated response with empty items list."""
        response = PaginatedResponse[dict](page=1, pages=1, per_page=10, total=0, items=[])

        assert response.total == 0
        assert len(response.items) == 0


class TestErrorResponse:
    """Test the ErrorResponse model."""

    def test_error_response_creation(self):
        """Test creating an error response."""
        error = ErrorResponse(
            error="Test error message",
            code="test_error",
            details={"field": "name", "value": "invalid"},
        )

        assert error.error == "Test error message"
        assert error.code == "test_error"
        assert error.details is not None
        assert error.details["field"] == "name"
        assert isinstance(error.timestamp, datetime)

    def test_error_response_minimal(self):
        """Test creating error response with minimal data."""
        error = ErrorResponse(error="Simple error")

        assert error.error == "Simple error"
        assert error.details is None
        assert error.code is None
        assert isinstance(error.timestamp, datetime)


class TestMessageResponse:
    """Test the MessageResponse model."""

    def test_message_response_creation(self):
        """Test creating a message response."""
        message = MessageResponse(message="Operation successful")

        assert message.message == "Operation successful"
        assert isinstance(message.timestamp, datetime)


class TestAuthToken:
    """Test the AuthToken model."""

    def test_auth_token_creation(self):
        """Test creating an auth token."""
        token = AuthToken(auth_token="abc123def456")

        assert token.auth_token == "abc123def456"


class TestBaseEntityModel:
    """Test the BaseEntityModel."""

    def test_base_entity_model_creation(self):
        """Test creating a base entity model."""
        entity = BaseEntityModel(
            id=1,
            created=datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC),
            updated=datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC),
        )

        assert entity.id == 1
        assert isinstance(entity.created, datetime)
        assert isinstance(entity.updated, datetime)

    def test_base_entity_model_optional_fields(self):
        """Test that all fields are optional in BaseEntityModel."""
        entity = BaseEntityModel()

        assert entity.id is None
        assert entity.created is None
        assert entity.updated is None


class TestBaseUUIDEntityModel:
    """Test the BaseUUIDEntityModel."""

    def test_base_uuid_entity_model_creation(self):
        """Test creating a base UUID entity model."""
        entity = BaseUUIDEntityModel(
            id="550e8400-e29b-41d4-a716-446655440000",
            created=datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC),
            updated=datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC),
        )

        assert entity.id == "550e8400-e29b-41d4-a716-446655440000"
        assert isinstance(entity.created, datetime)
        assert isinstance(entity.updated, datetime)


class TestErrorCreationUtilities:
    """Test error creation utility functions."""

    def test_create_validation_error(self):
        """Test creating a validation error."""
        error = create_validation_error("name", "cannot be empty")

        assert error.error == "Validation error in field 'name': cannot be empty"
        assert error.code == "validation_error"
        assert error.details is not None
        assert error.details["field"] == "name"
        assert error.details["message"] == "cannot be empty"

    def test_create_not_found_error(self):
        """Test creating a not found error."""
        error = create_not_found_error("Client", "123")

        assert error.error == "Client not found."
        assert error.code == "not_found"
        assert error.details is not None
        assert error.details["resource"] == "Client"
        assert error.details["identifier"] == "123"

    def test_create_generic_error(self):
        """Test creating a generic error."""
        error = create_generic_error(
            "Something went wrong", details={"context": "test"}, code="custom_error"
        )

        assert error.error == "Something went wrong"
        assert error.code == "custom_error"
        assert error.details is not None
        assert error.details["context"] == "test"


class TestValidationUtilities:
    """Test validation utility functions."""

    def test_validate_per_page_valid_values(self):
        """Test validate_per_page with valid values."""
        for valid_value in VALID_PER_PAGE_VALUES:
            result = validate_per_page(valid_value)
            assert result == valid_value

    def test_validate_per_page_invalid_value(self):
        """Test validate_per_page with invalid value."""
        with pytest.raises(ValueError) as exc_info:
            validate_per_page(15)  # Not in VALID_PER_PAGE_VALUES

        assert "must be one of" in str(exc_info.value)

    def test_validate_per_page_boundary_values(self):
        """Test validate_per_page with boundary values."""
        # Test minimum and maximum valid values
        min_valid = min(VALID_PER_PAGE_VALUES)
        max_valid = max(VALID_PER_PAGE_VALUES)

        assert validate_per_page(min_valid) == min_valid
        assert validate_per_page(max_valid) == max_valid


class TestConstants:
    """Test constants and configuration."""

    def test_valid_per_page_values(self):
        """Test that VALID_PER_PAGE_VALUES contains expected values."""
        expected_values = [2, 10, 20, 30, 40, 50, 100, 500, 1000, 5000, 10000, 100000]
        assert expected_values == VALID_PER_PAGE_VALUES

    def test_default_values(self):
        """Test default values are defined."""
        from aceiot_models.common import DEFAULT_PAGE, DEFAULT_PER_PAGE

        assert DEFAULT_PER_PAGE == 10
        assert DEFAULT_PAGE == 1
        assert DEFAULT_PER_PAGE in VALID_PER_PAGE_VALUES


class TestModelValidation:
    """Test model validation behavior."""

    def test_model_validation_on_assignment(self):
        """Test that validation occurs on assignment."""

        class TestModel(BaseModel):
            value: int

        model = TestModel(value=42)
        assert model.value == 42

        # This should trigger validation
        with pytest.raises(PydanticValidationError):
            model.value = "not an integer"  # type: ignore

    def test_model_populate_by_name(self):
        """Test populate_by_name configuration."""

        class TestModel(BaseModel):
            name: str
            value: int

        # Should work with field names
        model = TestModel(name="test", value=42)
        assert model.name == "test"
        assert model.value == 42

    def test_model_enum_values(self):
        """Test use_enum_values configuration."""
        from enum import Enum

        class Status(Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"

        class TestModel(BaseModel):
            status: Status

        model = TestModel(status=Status.ACTIVE)
        # With use_enum_values=True, we get the enum value, not the enum object
        assert model.status == "active"

        # Should serialize to enum value, not name
        data = model.model_dump()
        assert data["status"] == "active"


class TestModelSerialization:
    """Test model serialization behavior."""

    def test_datetime_serialization(self):
        """Test datetime serialization in JSON."""

        class TestModel(BaseModel):
            timestamp: datetime

        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)
        model = TestModel(timestamp=dt)

        # Test model_dump - our custom implementation converts datetime to ISO string
        data = model.model_dump()
        assert isinstance(data["timestamp"], str)
        assert data["timestamp"] == "2024-01-15T10:30:45+00:00"

        # Test JSON serialization
        json_str = model.model_dump_json()
        assert "2024-01-15T10:30:45" in json_str

    def test_optional_field_serialization(self):
        """Test optional field serialization."""

        class TestModel(BaseModel):
            required_field: str
            optional_field: str | None = None

        model = TestModel(required_field="test")

        # Test with exclude_none=False (default)
        data = model.model_dump()
        assert "optional_field" in data
        assert data["optional_field"] is None

        # Test with exclude_none=True
        data = model.model_dump(exclude_none=True)
        assert "optional_field" not in data
