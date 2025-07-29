"""Gateway models for ACE IoT API."""

from datetime import UTC, datetime
from typing import Any

from pydantic import Field, field_validator
from pydantic.networks import IPvAnyAddress

from .common import BaseEntityModel, BaseModel, PaginatedResponse


class GatewayBase(BaseModel):
    """Base gateway model with common fields."""

    name: str = Field(..., description="Gateway name", max_length=512)
    site_id: int | None = Field(None, description="ID of the site this gateway belongs to")
    client_id: int | None = Field(None, description="ID of the client this gateway belongs to")
    hw_type: str | None = Field(None, description="Hardware Type", max_length=512)
    software_type: str | None = Field(None, description="Software Type", max_length=512)
    primary_mac: str | None = Field(None, description="Primary MAC address", max_length=512)
    vpn_ip: IPvAnyAddress | None = Field(None, description="Overlay IP address")
    device_token: str | None = Field(None, description="Device Token", max_length=512)
    device_token_expires: datetime | None = Field(None, description="Gateway API Key Expiration")
    interfaces: dict[str, Any] | None = Field(None, description="Interface JSON Blob")
    deploy_config: dict[str, Any] | None = Field(
        None, description="Deployment Specific Config JSON Blob"
    )
    archived: bool | None = Field(False, description="Archived Gateway")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate gateway name is not empty and contains valid characters."""
        if not v or not v.strip():
            raise ValueError("Gateway name cannot be empty")

        v = v.strip()
        if len(v) < 2:
            raise ValueError("Gateway name must be at least 2 characters long")

        return v

    @field_validator("primary_mac")
    @classmethod
    def validate_mac_address(cls, v: str | None) -> str | None:
        """Validate MAC address format if provided."""
        if v is not None:
            v = v.strip()
            if v:
                # Basic MAC address validation (allow various formats)
                import re

                mac_patterns = [
                    r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",  # XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
                    r"^([0-9A-Fa-f]{2}){6}$",  # XXXXXXXXXXXX
                    r"^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$",  # XXXX.XXXX.XXXX
                ]

                if not any(re.match(pattern, v) for pattern in mac_patterns):
                    raise ValueError("Invalid MAC address format")

                return v
        return v

    @field_validator("device_token_expires")
    @classmethod
    def validate_token_expiry(cls, v: datetime | None) -> datetime | None:
        """Validate token expiry is in the future if provided."""
        if v is not None and v < datetime.now(UTC):
            raise ValueError("Device token expiry must be in the future")
        return v


class Gateway(GatewayBase, BaseEntityModel):
    """Full gateway model with all fields including ID and timestamps."""

    id: int | None = Field(None, description="Unique ID for gateway")
    site: str | None = Field(None, description="Site name")
    client: str | None = Field(None, description="Client Name")

    # Read-only fields from API
    hw_type: str | None = Field(None, description="Hardware Type")
    software_type: str | None = Field(None, description="Software Type")


class GatewayCreate(GatewayBase):
    """Gateway creation model - excludes ID and timestamps."""

    # Make site_id required for creation
    site_id: int | None = Field(None, description="ID of the site this gateway belongs to")
    client_id: int | None = Field(None, description="ID of the client this gateway belongs to")


class GatewayUpdate(BaseModel):
    """Gateway update model - all fields optional."""

    name: str | None = Field(None, description="Gateway name", max_length=512)
    site_id: int | None = Field(None, description="ID of the site this gateway belongs to")
    client_id: int | None = Field(None, description="ID of the client this gateway belongs to")
    primary_mac: str | None = Field(None, description="Primary MAC address", max_length=512)
    vpn_ip: IPvAnyAddress | None = Field(None, description="Overlay IP address")
    device_token: str | None = Field(None, description="Device Token", max_length=512)
    device_token_expires: datetime | None = Field(None, description="Gateway API Key Expiration")
    interfaces: dict[str, Any] | None = Field(None, description="Interface JSON Blob")
    deploy_config: dict[str, Any] | None = Field(
        None, description="Deployment Specific Config JSON Blob"
    )
    archived: bool | None = Field(None, description="Archived Gateway")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate gateway name if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Gateway name cannot be empty")

            v = v.strip()
            if len(v) < 2:
                raise ValueError("Gateway name must be at least 2 characters long")

        return v

    @field_validator("primary_mac")
    @classmethod
    def validate_mac_address(cls, v: str | None) -> str | None:
        """Validate MAC address format if provided."""
        if v is not None:
            v = v.strip()
            if v:
                import re

                mac_patterns = [
                    r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
                    r"^([0-9A-Fa-f]{2}){6}$",
                    r"^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$",
                ]

                if not any(re.match(pattern, v) for pattern in mac_patterns):
                    raise ValueError("Invalid MAC address format")

        return v


class GatewayResponse(Gateway):
    """Gateway response model - same as full Gateway model."""


class GatewayReference(BaseModel):
    """Minimal gateway reference for use in other models."""

    id: int = Field(..., description="Gateway ID")
    name: str = Field(..., description="Gateway name")


class GatewayList(BaseModel):
    """List of gateways wrapper."""

    gateways: list[Gateway] = Field(..., description="List of gateways")


class GatewayPaginatedResponse(PaginatedResponse[Gateway]):
    """Paginated response for gateways."""


class GatewayIdentity(BaseModel):
    """Gateway identity model for token generation."""

    model: str = Field(default="gateway", description="Model type")
    mac: str | None = Field(None, description="MAC address")
    id: int | None = Field(None, description="Gateway ID")
    name: str = Field(..., description="Gateway name")


# Utility functions for gateway operations
def create_gateway_not_found_error(gateway_identifier: str):
    """Create a standard gateway not found error."""
    from .common import create_not_found_error

    return create_not_found_error("Gateway", gateway_identifier)


def validate_gateway_name_uniqueness(name: str, existing_names: list[str]) -> bool:
    """Validate that gateway name is unique."""
    return name.lower().strip() not in [existing.lower().strip() for existing in existing_names]


def create_gateway_identity(gateway: Gateway) -> GatewayIdentity:
    """Create gateway identity dict for token generation."""
    return GatewayIdentity(
        model="gateway", mac=gateway.primary_mac, id=gateway.id, name=gateway.name
    )


def validate_interface_config(interfaces: dict[str, Any] | None) -> bool:
    """Validate interface configuration structure."""
    if interfaces is None:
        return True

    if not isinstance(interfaces, dict):
        raise ValueError("Interfaces must be a JSON object")

    # Add specific interface validation logic as needed
    return True


def validate_deploy_config(deploy_config: dict[str, Any] | None) -> bool:
    """Validate deployment configuration structure."""
    if deploy_config is None:
        return True

    if not isinstance(deploy_config, dict):
        raise ValueError("Deploy config must be a JSON object")

    # Add specific deploy config validation logic as needed
    return True


# Export all models
__all__ = [
    "Gateway",
    "GatewayBase",
    "GatewayCreate",
    "GatewayIdentity",
    "GatewayList",
    "GatewayPaginatedResponse",
    "GatewayReference",
    "GatewayResponse",
    "GatewayUpdate",
    "create_gateway_identity",
    "create_gateway_not_found_error",
    "validate_deploy_config",
    "validate_gateway_name_uniqueness",
    "validate_interface_config",
]
