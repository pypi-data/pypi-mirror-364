"""Point models for ACE IoT API."""

from typing import Any

from pydantic import Field, field_validator

from .common import BaseEntityModel, BaseModel, PaginatedResponse


class BACnetData(BaseModel):
    """BACnet communication related metadata."""

    device_address: str | None = Field(None, description="BACnet device address")
    device_id: int | None = Field(None, description="BACnet device ID")
    object_type: str | None = Field(None, description="BACnet object type")
    object_index: int | None = Field(None, description="BACnet object index")
    object_name: str | None = Field(None, description="BACnet object name")
    device_name: str | None = Field(None, description="BACnet device name")
    object_description: str | None = Field(None, description="BACnet object description")
    device_description: str | None = Field(None, description="BACnet device description")
    scrape_interval: int | None = Field(None, description="Scrape interval in seconds")
    scrape_enabled: bool | None = Field(None, description="Enable BACnet scraping")
    present_value: str | None = Field(None, description="Current/present value")
    additional_properties: dict[str, str] | None = Field(
        None, description="Additional BACnet properties"
    )

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, v: int | None) -> int | None:
        """Validate BACnet device ID is within valid range."""
        if v is not None and (v < 0 or v > 4194303):  # BACnet device ID range 0-4194303
            raise ValueError("BACnet device ID must be between 0 and 4194303")
        return v

    @field_validator("object_index")
    @classmethod
    def validate_object_index(cls, v: int | None) -> int | None:
        """Validate BACnet object index is positive."""
        if v is not None and v < 0:
            raise ValueError("BACnet object index must be non-negative")
        return v

    @field_validator("scrape_interval")
    @classmethod
    def validate_scrape_interval(cls, v: int | None) -> int | None:
        """Validate scrape interval is positive."""
        if v is not None and v <= 0:
            raise ValueError("Scrape interval must be positive")
        return v


class PointBase(BaseModel):
    """Base point model with common fields."""

    name: str = Field(..., description="Point name", max_length=512)
    site_id: int = Field(..., description="ID of the site this point belongs to")
    client_id: int = Field(..., description="ID of the client this point belongs to")
    marker_tags: list[str] | None = Field(default_factory=list, description="Marker tags")
    kv_tags: dict[str, str] | None = Field(
        default_factory=dict, description="Arbitrary key value tags, strings only"
    )
    bacnet_data: BACnetData | None = Field(
        None, description="BACnet communication related metadata"
    )
    collect_config: dict[str, Any] | None = Field(
        default_factory=dict, description="Config fragment for specific point type"
    )
    point_type: str | None = Field(
        None, description="Type of point for encoding/decoding configs", max_length=256
    )
    collect_enabled: bool | None = Field(False, description="Enable collection of data")
    collect_interval: int | None = Field(None, description="Interval for collection in seconds")
    topic_id: int | None = Field(None, description="Topic ID for VOLTTRON")
    device_id: str | None = Field(None, description="Device UUID")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate point name is not empty and contains valid characters."""
        if not v or not v.strip():
            raise ValueError("Point name cannot be empty")

        v = v.strip()
        if len(v) < 2:
            raise ValueError("Point name must be at least 2 characters long")

        return v

    @field_validator("marker_tags")
    @classmethod
    def validate_marker_tags(cls, v: list[str] | None) -> list[str]:
        """Validate marker tags are strings and not empty."""
        if v is None:
            return []

        validated_tags = []
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError("All marker tags must be strings")
            tag = tag.strip()
            if tag:  # Only add non-empty tags
                validated_tags.append(tag)

        return validated_tags

    @field_validator("kv_tags")
    @classmethod
    def validate_kv_tags(cls, v: dict[str, str] | None) -> dict[str, str]:
        """Validate key-value tags are string->string mappings."""
        if v is None:
            return {}

        validated_tags = {}
        for key, value in v.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("All key-value tags must be string->string mappings")

            key = key.strip()
            value = value.strip()
            if key and value:  # Only add non-empty key-value pairs
                validated_tags[key] = value

        return validated_tags

    @field_validator("collect_interval")
    @classmethod
    def validate_collect_interval(cls, v: int | None) -> int | None:
        """Validate collection interval is positive."""
        if v is not None and v <= 0:
            raise ValueError("Collection interval must be positive")
        return v


class Point(PointBase, BaseEntityModel):
    """Full point model with all fields including ID and timestamps."""

    id: int | None = Field(None, description="Unique ID for point")
    client: str | None = Field(None, description="Client this point belongs to")
    site: str | None = Field(None, description="Site this point belongs to")


class PointCreate(PointBase):
    """Point creation model - excludes ID and timestamps."""


class PointUpdate(BaseModel):
    """Point update model - all fields optional."""

    name: str | None = Field(None, description="Point name", max_length=512)
    site_id: int | None = Field(None, description="ID of the site this point belongs to")
    client_id: int | None = Field(None, description="ID of the client this point belongs to")
    marker_tags: list[str] | None = Field(None, description="Marker tags")
    kv_tags: dict[str, str] | None = Field(
        None, description="Arbitrary key value tags, strings only"
    )
    bacnet_data: BACnetData | None = Field(
        None, description="BACnet communication related metadata"
    )
    collect_config: dict[str, Any] | None = Field(
        None, description="Config fragment for specific point type"
    )
    point_type: str | None = Field(
        None, description="Type of point for encoding/decoding configs", max_length=256
    )
    collect_enabled: bool | None = Field(None, description="Enable collection of data")
    collect_interval: int | None = Field(None, description="Interval for collection in seconds")
    topic_id: int | None = Field(None, description="Topic ID for VOLTTRON")
    device_id: str | None = Field(None, description="Device UUID")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate point name if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Point name cannot be empty")

            v = v.strip()
            if len(v) < 2:
                raise ValueError("Point name must be at least 2 characters long")

        return v

    @field_validator("marker_tags")
    @classmethod
    def validate_marker_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate marker tags if provided."""
        if v is not None:
            validated_tags = []
            for tag in v:
                if not isinstance(tag, str):
                    raise ValueError("All marker tags must be strings")
                tag = tag.strip()
                if tag:
                    validated_tags.append(tag)
            return validated_tags
        return v

    @field_validator("kv_tags")
    @classmethod
    def validate_kv_tags(cls, v: dict[str, str] | None) -> dict[str, str] | None:
        """Validate key-value tags if provided."""
        if v is not None:
            validated_tags = {}
            for key, value in v.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError("All key-value tags must be string->string mappings")

                key = key.strip()
                value = value.strip()
                if key and value:
                    validated_tags[key] = value
            return validated_tags
        return v


class PointResponse(Point):
    """Point response model - same as full Point model."""


class PointReference(BaseModel):
    """Minimal point reference for use in other models."""

    id: int = Field(..., description="Point ID")
    name: str = Field(..., description="Point name")


class PointList(BaseModel):
    """List of points wrapper."""

    points: list[Point] = Field(..., description="List of points")


class PointPaginatedResponse(PaginatedResponse[Point]):
    """Paginated response for points."""


# Utility functions for point operations
def create_point_not_found_error(point_identifier: str):
    """Create a standard point not found error."""
    from .common import create_not_found_error

    return create_not_found_error("Point", point_identifier)


def validate_point_name_uniqueness(name: str, existing_names: list[str]) -> bool:
    """Validate that point name is unique within its scope."""
    return name.lower().strip() not in [existing.lower().strip() for existing in existing_names]


def merge_marker_tags(
    existing_tags: list[str], new_tags: list[str], overwrite: bool = False
) -> list[str]:
    """Merge marker tags with option to overwrite."""
    if overwrite:
        return new_tags

    # Combine and deduplicate tags
    combined_tags = list(set(existing_tags + new_tags))
    return sorted(combined_tags)


def merge_kv_tags(
    existing_tags: dict[str, str], new_tags: dict[str, str], overwrite: bool = False
) -> dict[str, str]:
    """Merge key-value tags with option to overwrite."""
    if overwrite:
        return new_tags

    # Merge dictionaries, new tags override existing ones with same keys
    merged_tags = existing_tags.copy()
    merged_tags.update(new_tags)
    return merged_tags


def validate_collect_config_for_point_type(
    point_type: str | None, collect_config: dict[str, Any]
) -> bool:
    """Validate collection configuration is appropriate for point type."""
    if point_type is None:
        return True

    # Add point-type specific validation logic here
    # For now, just validate it's a dictionary
    if not isinstance(collect_config, dict):
        raise ValueError("Collection config must be a JSON object")

    return True


# Export all models
__all__ = [
    "BACnetData",
    "Point",
    "PointBase",
    "PointCreate",
    "PointList",
    "PointPaginatedResponse",
    "PointReference",
    "PointResponse",
    "PointUpdate",
    "create_point_not_found_error",
    "merge_kv_tags",
    "merge_marker_tags",
    "validate_collect_config_for_point_type",
    "validate_point_name_uniqueness",
]
