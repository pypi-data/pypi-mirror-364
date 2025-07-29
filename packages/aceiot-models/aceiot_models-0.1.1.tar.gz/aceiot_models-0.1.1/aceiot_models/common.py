"""Common base models and utilities used across ACE IoT models."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, ValidationInfo, field_validator
from pydantic.networks import IPvAnyAddress


# Configure Pydantic settings
class BaseModel(PydanticBaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        # Enable ORM mode for SQLAlchemy compatibility
        from_attributes=True,
        # Validate on assignment
        validate_assignment=True,
        # Use enum values instead of names
        use_enum_values=True,
        # Allow population by field name or alias
        populate_by_name=True,
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Custom model dump with datetime serialization."""
        data = super().model_dump(**kwargs)
        # Convert datetime objects to ISO format
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() if value else None
        return data


class PaginatedResponse[T](BaseModel):
    """Paginated response model following the API specification."""

    page: int = Field(..., description="Number of this page of results")
    pages: int = Field(..., description="Total number of pages of results")
    per_page: int = Field(..., description="Number of items per page of results")
    total: int = Field(..., description="Total number of results")
    items: list[T] = Field(..., description="Items in this page")

    @field_validator("page", "pages", "per_page", "total")
    @classmethod
    def validate_positive_integers(cls, v: int) -> int:
        """Validate that pagination fields are positive integers."""
        if v < 0:
            raise ValueError("Pagination fields must be non-negative integers")
        return v

    @field_validator("page")
    @classmethod
    def validate_page_number(cls, v: int, info: ValidationInfo) -> int:
        """Validate that page number is within valid range."""
        if hasattr(info, "data") and info.data and "pages" in info.data:
            pages = info.data["pages"]
            if v > pages and pages > 0:
                raise ValueError(f"Page number {v} exceeds total pages {pages}")
        return v


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
    code: str | None = Field(None, description="Error code")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Error timestamp"
    )


class MessageResponse(BaseModel):
    """Standard success message response."""

    message: str = Field(..., description="Success message")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Response timestamp"
    )


class AuthToken(BaseModel):
    """Authorization token model."""

    auth_token: str = Field(
        ..., description="An authorization token used to access ACE Manager API"
    )


class IPAddressModel(BaseModel):
    """IP address model with optional subnet mask."""

    ip_address: IPvAnyAddress = Field(..., description="IP address")
    subnet_mask: str | None = Field(None, description="Optional subnet mask")


class FileMetadata(BaseModel):
    """File metadata model."""

    filename: str = Field(..., description="Name of the file")
    size: int | None = Field(None, description="File size in bytes")
    content_type: str | None = Field(None, description="MIME content type")
    upload_time: datetime | None = Field(None, description="Upload timestamp")

    @field_validator("size")
    @classmethod
    def validate_file_size(cls, v: int | None) -> int | None:
        """Validate file size is positive."""
        if v is not None and v < 0:
            raise ValueError("File size must be non-negative")
        return v


class BaseEntityModel(BaseModel):
    """Base model for entities with common fields."""

    id: int | None = Field(None, description="Unique identifier")
    created: datetime | None = Field(None, description="Date created in ISO8601 format")
    updated: datetime | None = Field(None, description="Last updated in ISO8601 format")


class BaseUUIDEntityModel(BaseModel):
    """Base model for entities with UUID identifiers."""

    id: str | None = Field(None, description="Unique UUID identifier")
    created: datetime | None = Field(None, description="Date created in ISO8601 format")
    updated: datetime | None = Field(None, description="Last updated in ISO8601 format")


# Utility functions for error handling
def create_validation_error(
    field: str, message: str, code: str = "validation_error"
) -> ErrorResponse:
    """Create a standardized validation error response."""
    return ErrorResponse(
        error=f"Validation error in field '{field}': {message}",
        details={"field": field, "message": message},
        code=code,
    )


def create_not_found_error(resource: str, identifier: str) -> ErrorResponse:
    """Create a standardized not found error response."""
    return ErrorResponse(
        error=f"{resource} not found.",
        details={"resource": resource, "identifier": identifier},
        code="not_found",
    )


def create_generic_error(
    message: str, details: dict[str, Any] | None = None, code: str = "generic_error"
) -> ErrorResponse:
    """Create a generic error response."""
    return ErrorResponse(error=message, details=details, code=code)


# Constants for validation
VALID_PER_PAGE_VALUES = [2, 10, 20, 30, 40, 50, 100, 500, 1000, 5000, 10000, 100000]
DEFAULT_PER_PAGE = 10
DEFAULT_PAGE = 1


def validate_per_page(per_page: int) -> int:
    """Validate per_page parameter against allowed values."""
    if per_page not in VALID_PER_PAGE_VALUES:
        raise ValueError(f"per_page must be one of {VALID_PER_PAGE_VALUES}")
    return per_page
