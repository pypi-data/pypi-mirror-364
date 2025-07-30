"""Sample model for time-series data."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from aceiot_models.common import BaseModel
from aceiot_models.validators import validate_float, validate_non_empty_string


class SampleBase(BaseModel):
    """Base model for time-series data samples."""

    name: str = Field(..., description="The name identifier for this sample")
    time: datetime = Field(..., description="The timestamp when this sample was recorded")
    value: float = Field(..., description="The numeric value of this sample")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate sample name is non-empty."""
        return validate_non_empty_string(v, "name")

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float) -> float:
        """Validate sample value is a valid float."""
        return validate_float(v, "value")


class Sample(SampleBase):
    """Represents a time-series data sample."""

    @classmethod
    def from_api_model(cls, sample: dict[str, Any]) -> Sample:
        """Create a Sample instance from API response data.

        Args:
            sample: Dictionary containing sample data from API

        Returns:
            Sample instance
        """
        return cls(
            name=sample["name"],
            time=datetime.fromisoformat(sample["time"]),
            value=sample["value"],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert Sample to dictionary for serialization.

        Returns:
            Dictionary representation of the sample
        """
        return {
            "name": self.name,
            "time": self.time.isoformat().replace("+00:00", "Z"),
            "value": self.value,
        }


class SampleCreate(SampleBase):
    """Model for creating a new sample."""


class SampleUpdate(BaseModel):
    """Model for updating an existing sample."""

    name: str | None = Field(None, description="The name identifier for this sample")
    time: datetime | None = Field(None, description="The timestamp when this sample was recorded")
    value: float | None = Field(None, description="The numeric value of this sample")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate sample name is non-empty if provided."""
        if v is None:
            return v
        return validate_non_empty_string(v, "name")

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float | None) -> float | None:
        """Validate sample value is a valid float if provided."""
        if v is None:
            return v
        return validate_float(v, "value")


class SampleResponse(Sample):
    """API response model for a sample."""


class SampleList(BaseModel):
    """List of samples response model."""

    samples: list[Sample] = Field(default_factory=list, description="List of samples")
    count: int = Field(..., description="Total number of samples")


__all__ = [
    "Sample",
    "SampleBase",
    "SampleCreate",
    "SampleList",
    "SampleResponse",
    "SampleUpdate",
]
