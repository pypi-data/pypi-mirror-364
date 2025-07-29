"""Site models for ACE IoT API."""

from pydantic import Field, field_validator
from pydantic.networks import IPvAnyAddress

from .common import BaseEntityModel, BaseModel, PaginatedResponse


class SiteBase(BaseModel):
    """Base site model with common fields."""

    name: str = Field(..., description="Unique path for site", max_length=512)
    nice_name: str | None = Field(None, description="Nice Name for Site", max_length=512)
    address: str | None = Field(None, description="Address for Site", max_length=512)
    vtron_ip: IPvAnyAddress | None = Field(None, description="Volttron IP address")
    vtron_user: str | None = Field(None, description="Volttron run as user", max_length=256)
    ansible_user: str | None = Field(
        None, description="ansible user for deploy tasks", max_length=256
    )
    latitude: float | None = Field(None, description="latitude of site in degrees")
    longitude: float | None = Field(None, description="longitude of site in degrees")
    geo_location: str | None = Field(None, description="Geographic Location")
    mqtt_prefix: str | None = Field(None, description="Mqtt Prefix", max_length=256)
    client_id: int = Field(..., description="ID of the client this site belongs to")
    archived: bool | None = Field(False, description="Archived Site")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate site name is not empty and follows path conventions."""
        if not v or not v.strip():
            raise ValueError("Site name cannot be empty")

        # Remove leading/trailing whitespace
        v = v.strip()

        if len(v) < 2:
            raise ValueError("Site name must be at least 2 characters long")

        # Site names should be path-safe (no spaces, special chars for URL compatibility)
        invalid_chars = [
            " ",
            "/",
            "\\",
            "?",
            "#",
            "[",
            "]",
            "@",
            "!",
            "$",
            "&",
            "'",
            "(",
            ")",
            "*",
            "+",
            ",",
            ";",
            "=",
        ]
        if any(char in v for char in invalid_chars):
            raise ValueError(
                f"Site name cannot contain spaces or special characters: {invalid_chars}"
            )

        return v

    @field_validator("nice_name")
    @classmethod
    def validate_nice_name(cls, v: str | None) -> str | None:
        """Validate nice name if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) < 2:
                raise ValueError("Nice name must be at least 2 characters long if provided")
        return v

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float | None) -> float | None:
        """Validate latitude is within valid range."""
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float | None) -> float | None:
        """Validate longitude is within valid range."""
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return v


class Site(SiteBase, BaseEntityModel):
    """Full site model with all fields including ID and timestamps."""

    id: int | None = Field(None, description="Unique ID for site")
    client: str | None = Field(None, description="client display name")


class SiteCreate(SiteBase):
    """Site creation model - excludes ID and timestamps."""


class SiteUpdate(BaseModel):
    """Site update model - all fields optional except client_id validation."""

    name: str | None = Field(None, description="Unique path for site", max_length=512)
    nice_name: str | None = Field(None, description="Nice Name for Site", max_length=512)
    address: str | None = Field(None, description="Address for Site", max_length=512)
    vtron_ip: IPvAnyAddress | None = Field(None, description="Volttron IP address")
    vtron_user: str | None = Field(None, description="Volttron run as user", max_length=256)
    ansible_user: str | None = Field(
        None, description="ansible user for deploy tasks", max_length=256
    )
    latitude: float | None = Field(None, description="latitude of site in degrees")
    longitude: float | None = Field(None, description="longitude of site in degrees")
    geo_location: str | None = Field(None, description="Geographic Location")
    mqtt_prefix: str | None = Field(None, description="Mqtt Prefix", max_length=256)
    client_id: int | None = Field(None, description="ID of the client this site belongs to")
    archived: bool | None = Field(None, description="Archived Site")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate site name if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Site name cannot be empty")

            v = v.strip()
            if len(v) < 2:
                raise ValueError("Site name must be at least 2 characters long")

            invalid_chars = [
                " ",
                "/",
                "\\",
                "?",
                "#",
                "[",
                "]",
                "@",
                "!",
                "$",
                "&",
                "'",
                "(",
                ")",
                "*",
                "+",
                ",",
                ";",
                "=",
            ]
            if any(char in v for char in invalid_chars):
                raise ValueError(
                    f"Site name cannot contain spaces or special characters: {invalid_chars}"
                )

        return v

    @field_validator("nice_name")
    @classmethod
    def validate_nice_name(cls, v: str | None) -> str | None:
        """Validate nice name if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) < 2:
                raise ValueError("Nice name must be at least 2 characters long if provided")
        return v


class SiteResponse(Site):
    """Site response model - same as full Site model."""


class SiteReference(BaseModel):
    """Minimal site reference for use in other models."""

    id: int = Field(..., description="Site ID")
    name: str = Field(..., description="Site name")


class SiteList(BaseModel):
    """List of sites wrapper."""

    sites: list[Site] = Field(..., description="List of sites")


class SitePaginatedResponse(PaginatedResponse[Site]):
    """Paginated response for sites."""


# Utility functions for site operations
def create_site_not_found_error(site_identifier: str):
    """Create a standard site not found error."""
    from .common import create_not_found_error

    return create_not_found_error("Site", site_identifier)


def validate_site_name_uniqueness(name: str, existing_names: list[str]) -> bool:
    """Validate that site name is unique."""
    return name.lower().strip() not in [existing.lower().strip() for existing in existing_names]


def validate_coordinates(latitude: float | None, longitude: float | None) -> bool:
    """Validate that if one coordinate is provided, both should be provided."""
    if (latitude is None) != (longitude is None):
        raise ValueError(
            "Both latitude and longitude must be provided together, or both should be None"
        )
    return True


# Export all models
__all__ = [
    "Site",
    "SiteBase",
    "SiteCreate",
    "SiteList",
    "SitePaginatedResponse",
    "SiteReference",
    "SiteResponse",
    "SiteUpdate",
    "create_site_not_found_error",
    "validate_coordinates",
    "validate_site_name_uniqueness",
]
