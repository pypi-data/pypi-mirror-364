"""DER Event models for ACE IoT API."""

from datetime import datetime

import pytz
from pydantic import Field, field_validator

from .common import BaseModel, BaseUUIDEntityModel, PaginatedResponse


class DerEventBase(BaseModel):
    """Base DER event model with common fields."""

    timezone: str = Field(..., description="Timezone for the event")
    event_start: datetime = Field(..., description="Event start time")
    event_end: datetime = Field(..., description="Event end time")
    event_type: str = Field(..., description="Type of DER event")
    group_name: str | None = Field(None, description="Group name for the event")
    cancelled: bool | None = Field(False, description="Whether the event is cancelled")
    title: str | None = Field(None, description="Event Title")
    description: str | None = Field(None, description="Event description")

    @field_validator("event_start", "event_end")
    @classmethod
    def validate_datetime_not_none(cls, v: datetime) -> datetime:
        """Validate datetime fields are not None."""
        if v is None:
            raise ValueError("Event start and end times are required")
        return v

    @field_validator("event_end")
    @classmethod
    def validate_end_after_start(cls, v: datetime, values) -> datetime:
        """Validate that event end time is after start time."""
        if hasattr(values, "data") and "event_start" in values.data:
            event_start = values.data["event_start"]
            if event_start and v <= event_start:
                raise ValueError("Event end time must be after start time")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate timezone is not empty."""
        if not v or not v.strip():
            raise ValueError("Timezone cannot be empty")

        # Basic timezone validation - could be enhanced with pytz validation
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Invalid timezone format")

        return v

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        """Validate event type is not empty."""
        if not v or not v.strip():
            raise ValueError("Event type cannot be empty")
        return v.strip()

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Validate title if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate description if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class DerEvent(DerEventBase, BaseUUIDEntityModel):
    """Full DER event model with all fields including ID and timestamps."""

    id: str | None = Field(None, description="Unique UUID for DER event")
    client: str | None = Field(None, description="Client name")
    created_by_user: str | None = Field(None, description="User who created the event")


class DerEventCreate(DerEventBase):
    """DER event creation model - excludes ID and timestamps."""

    client_id: int | None = Field(None, description="ID of the client this event belongs to")
    created_by_user: str | None = Field(None, description="User creating the event")


class DerEventUpdate(BaseModel):
    """DER event update model - all fields optional except ID."""

    id: int = Field(..., description="Event ID")
    timezone: str | None = Field(None, description="Timezone for the event")
    event_start: datetime | None = Field(None, description="Event start time")
    event_end: datetime | None = Field(None, description="Event end time")
    event_type: str | None = Field(None, description="Type of DER event")
    group_name: str | None = Field(None, description="Group name for the event")
    cancelled: bool | None = Field(None, description="Whether the event is cancelled")
    title: str | None = Field(None, description="Event Title")
    description: str | None = Field(None, description="Event description")

    @field_validator("event_end")
    @classmethod
    def validate_end_after_start(cls, v: datetime | None, values) -> datetime | None:
        """Validate that event end time is after start time if both are provided."""
        if v is not None and hasattr(values, "data") and "event_start" in values.data:
            event_start = values.data["event_start"]
            if event_start and v <= event_start:
                raise ValueError("Event end time must be after start time")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str | None) -> str | None:
        """Validate timezone if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Timezone cannot be empty")

            v = v.strip()
            if len(v) < 3:
                raise ValueError("Invalid timezone format")

        return v

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str | None) -> str | None:
        """Validate event type if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Event type cannot be empty")
            return v.strip()
        return v


class DerEventResponse(DerEvent):
    """DER event response model - same as full DerEvent model."""


class DerEventReference(BaseModel):
    """Minimal DER event reference for use in other models."""

    id: str = Field(..., description="DER event UUID")
    title: str | None = Field(None, description="Event title")
    event_type: str = Field(..., description="Event type")


class DerEventList(BaseModel):
    """List of DER events wrapper."""

    der_events: list[DerEvent] = Field(..., description="List of DER events")


class DerEventCreateList(BaseModel):
    """List of DER events for bulk creation."""

    der_events: list[DerEventCreate] = Field(..., description="List of DER events to create")


class DerEventUpdateList(BaseModel):
    """List of DER events for bulk updates."""

    der_events: list[DerEventUpdate] = Field(..., description="List of DER events to update")

    @field_validator("der_events")
    @classmethod
    def validate_events_have_ids(cls, v: list[DerEventUpdate]) -> list[DerEventUpdate]:
        """Validate that all events in update list have IDs."""
        for event in v:
            if not hasattr(event, "id") or not event.id:
                raise ValueError("All events in update list must have IDs")
        return v


class DerEventPaginatedResponse(PaginatedResponse[DerEvent]):
    """Paginated response for DER events."""


# Utility functions for DER event operations
def create_der_event_not_found_error(event_identifier: str):
    """Create a standard DER event not found error."""
    from .common import create_not_found_error

    return create_not_found_error("DER Event", event_identifier)


def validate_event_time_range(start: datetime, end: datetime) -> bool:
    """Validate that event time range is valid."""
    if start >= end:
        raise ValueError("Event start time must be before end time")

    # Check for reasonable duration (not more than 1 year)
    duration = end - start
    if duration.days > 365:
        raise ValueError("Event duration cannot exceed 365 days")

    return True


def validate_timezone_format(timezone: str) -> bool:
    """Validate timezone format (basic validation)."""
    try:
        # Validate timezone with pytz
        pytz.timezone(timezone)
        return True
    except ImportError:
        # Fallback to basic string validation if pytz not available
        if not timezone or len(timezone) < 3:
            raise ValueError("Invalid timezone format") from None
        return True
    except Exception:
        raise ValueError(f"Invalid timezone: {timezone}") from None


def check_event_overlap(event1: DerEventBase, event2: DerEventBase) -> bool:
    """Check if two events overlap in time."""
    return not (event1.event_end <= event2.event_start or event2.event_end <= event1.event_start)


def get_event_duration_hours(event: DerEventBase) -> float:
    """Get event duration in hours."""
    duration = event.event_end - event.event_start
    return duration.total_seconds() / 3600


# Export all models
__all__ = [
    "DerEvent",
    "DerEventBase",
    "DerEventCreate",
    "DerEventCreateList",
    "DerEventList",
    "DerEventPaginatedResponse",
    "DerEventReference",
    "DerEventResponse",
    "DerEventUpdate",
    "DerEventUpdateList",
    "check_event_overlap",
    "create_der_event_not_found_error",
    "get_event_duration_hours",
    "validate_event_time_range",
    "validate_timezone_format",
]
