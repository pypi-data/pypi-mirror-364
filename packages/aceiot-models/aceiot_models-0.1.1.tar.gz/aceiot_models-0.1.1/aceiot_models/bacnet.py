"""BACnet-specific models for aceiot-models."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from aceiot_models.common import BaseEntityModel, BaseModel
from aceiot_models.validators import (
    validate_integer_range,
    validate_non_empty_string,
)


logger = logging.getLogger(__name__)

# Device address normalization mapping
DEVICE_ADDRESS_NORMALIZE_MAP = str.maketrans({"_": ".", ",": None, " ": "."})


class BACnetDeviceBase(BaseModel):
    """Base model for BACnet devices."""

    client: str = Field(..., description="Client identifier for this device")
    site: str = Field(..., description="Site where this device is located")
    device_id: int = Field(..., description="BACnet device instance number (0-4194303)")
    device_address: str = Field(..., description="Network address of the BACnet device")
    device_name: str = Field(..., description="Human-readable name of the device")
    device_description: str = Field("", description="Description of the device")
    proxy_id: str = Field(
        "platform.bacnet_proxy", description="Identifier of the BACnet proxy managing this device"
    )

    @field_validator("client")
    @classmethod
    def validate_client(cls, v: str) -> str:
        """Validate client is non-empty."""
        result = validate_non_empty_string(v, "client")
        if result is None:
            raise ValueError("client cannot be None")
        return result

    @field_validator("site")
    @classmethod
    def validate_site(cls, v: str) -> str:
        """Validate site is non-empty."""
        result = validate_non_empty_string(v, "site")
        if result is None:
            raise ValueError("site cannot be None")
        return result

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, v: int) -> int:
        """Validate device_id is within BACnet range."""
        result = validate_integer_range(v, "device_id", min_value=0, max_value=4194303)
        if result is None:
            raise ValueError("device_id cannot be None")
        return result

    @field_validator("device_address")
    @classmethod
    def validate_device_address(cls, v: str) -> str:
        """Validate device_address is non-empty."""
        result = validate_non_empty_string(v, "device_address")
        if result is None:
            raise ValueError("device_address cannot be None")
        return result

    @field_validator("device_name")
    @classmethod
    def validate_device_name(cls, v: str) -> str:
        """Validate device_name is non-empty."""
        result = validate_non_empty_string(v, "device_name")
        if result is None:
            raise ValueError("device_name cannot be None")
        return result


class BACnetDevice(BACnetDeviceBase, BaseEntityModel):
    """Represents a BACnet device with normalization and serialization capabilities."""

    last_seen: datetime | None = Field(None, description="Last time this device was seen online")
    last_scanned: datetime | None = Field(None, description="Last time this device was scanned")

    def normalize_address(self) -> str:
        """Normalize the device address for consistent identification.

        Returns:
            Normalized address string
        """
        return f"{self.device_address}-{self.device_id}".translate(DEVICE_ADDRESS_NORMALIZE_MAP)

    def serialize_device_path(self) -> str:
        """Create a hierarchical device path.

        Returns:
            Device path in format: client/site/normalized_address
        """
        return f"{self.client}/{self.site}/{self.normalize_address()}"

    @classmethod
    def from_api_point(cls, point: dict[str, Any]) -> BACnetDevice:
        """Create a BACnetDevice from point data.

        Args:
            point: Dictionary containing point data with bacnet_data

        Returns:
            BACnetDevice instance
        """
        bacnet_data = point.get("bacnet_data", {})
        return cls(
            client=point["client"],
            site=point["site"],
            device_name=bacnet_data.get("device_name", ""),
            device_id=bacnet_data["device_id"],
            device_address=bacnet_data["device_address"],
            device_description=bacnet_data.get("device_description", ""),
            proxy_id=bacnet_data.get("bacnet_proxy", "platform.bacnet_proxy"),
            last_seen=None,
            last_scanned=None,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert BACnetDevice to dictionary for serialization.

        Returns:
            Dictionary representation of the device
        """
        return {
            "client": self.client,
            "site": self.site,
            "device_id": self.device_id,
            "device_address": self.device_address,
            "device_name": self.device_name,
            "device_description": self.device_description,
            "proxy_id": self.proxy_id,
            "last_seen": self.last_seen.isoformat().replace("+00:00", "Z")
            if self.last_seen
            else None,
            "last_scanned": self.last_scanned.isoformat().replace("+00:00", "Z")
            if self.last_scanned
            else None,
        }


class BACnetDeviceCreate(BACnetDeviceBase):
    """Model for creating a new BACnet device."""

    last_seen: datetime | None = Field(None, description="Last time this device was seen online")
    last_scanned: datetime | None = Field(None, description="Last time this device was scanned")


class BACnetDeviceUpdate(BaseModel):
    """Model for updating an existing BACnet device."""

    client: str | None = Field(None, description="Client identifier for this device")
    site: str | None = Field(None, description="Site where this device is located")
    device_id: int | None = Field(None, description="BACnet device instance number (0-4194303)")
    device_address: str | None = Field(None, description="Network address of the BACnet device")
    device_name: str | None = Field(None, description="Human-readable name of the device")
    device_description: str | None = Field(None, description="Description of the device")
    proxy_id: str | None = Field(
        None, description="Identifier of the BACnet proxy managing this device"
    )
    last_seen: datetime | None = Field(None, description="Last time this device was seen online")
    last_scanned: datetime | None = Field(None, description="Last time this device was scanned")

    @field_validator("client")
    @classmethod
    def validate_client(cls, v: str | None) -> str | None:
        """Validate client is non-empty if provided."""
        if v is None:
            return v
        return validate_non_empty_string(v, "client")

    @field_validator("site")
    @classmethod
    def validate_site(cls, v: str | None) -> str | None:
        """Validate site is non-empty if provided."""
        if v is None:
            return v
        return validate_non_empty_string(v, "site")

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, v: int | None) -> int | None:
        """Validate device_id is within BACnet range if provided."""
        if v is None:
            return v
        return validate_integer_range(v, "device_id", min_value=0, max_value=4194303)

    @field_validator("device_address")
    @classmethod
    def validate_device_address(cls, v: str | None) -> str | None:
        """Validate device_address is non-empty if provided."""
        if v is None:
            return v
        return validate_non_empty_string(v, "device_address")

    @field_validator("device_name")
    @classmethod
    def validate_device_name(cls, v: str | None) -> str | None:
        """Validate device_name is non-empty if provided."""
        if v is None:
            return v
        return validate_non_empty_string(v, "device_name")


class BACnetDeviceResponse(BACnetDevice):
    """API response model for a BACnet device."""


class BACnetDeviceReference(BaseModel):
    """Minimal reference model for a BACnet device."""

    id: int = Field(..., description="Unique identifier for this device")
    device_name: str = Field(..., description="Human-readable name of the device")
    device_id: int = Field(..., description="BACnet device instance number")


class BACnetPointBase(BaseModel):
    """Base model for BACnet points."""

    name: str = Field(..., description="Unique name for this point")
    point_type: str = Field("bacnet", description="Type of point (e.g., 'bacnet')")
    marker_tags: list[str] = Field(default_factory=list, description="List of marker tags")
    kv_tags: dict[str, str] = Field(default_factory=dict, description="Key-value tag pairs")
    collect_config: dict[str, Any] = Field(
        default_factory=dict, description="Collection configuration"
    )
    object_type: str = Field(..., description="BACnet object type (e.g., 'analogInput')")
    object_index: str = Field(..., description="BACnet object instance number")
    object_units: str | None = Field(None, description="Engineering units for this object")
    object_name: str = Field(..., description="BACnet object name")
    object_description: str = Field("", description="BACnet object description")
    present_value: str = Field(..., description="Current value of the BACnet object")
    raw_properties: dict[str, Any] = Field(
        default_factory=dict, description="Raw BACnet properties"
    )
    collect_enabled: bool = Field(False, description="Whether collection is enabled for this point")
    collect_interval: int = Field(300, description="Collection interval in seconds")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is non-empty."""
        return validate_non_empty_string(v, "name")

    @field_validator("object_type")
    @classmethod
    def validate_object_type(cls, v: str) -> str:
        """Validate object_type is non-empty."""
        return validate_non_empty_string(v, "object_type")

    @field_validator("object_index")
    @classmethod
    def validate_object_index(cls, v: str) -> str:
        """Validate object_index is non-empty."""
        return validate_non_empty_string(v, "object_index")

    @field_validator("object_name")
    @classmethod
    def validate_object_name(cls, v: str) -> str:
        """Validate object_name is non-empty."""
        return validate_non_empty_string(v, "object_name")

    @field_validator("collect_interval")
    @classmethod
    def validate_collect_interval(cls, v: int) -> int:
        """Validate collect_interval is positive."""
        if v <= 0:
            raise ValueError("collect_interval must be positive")
        return v


class BACnetPoint(BACnetPointBase, BaseEntityModel):
    """Represents a BACnet point with full device context and properties."""

    device: BACnetDevice = Field(..., description="The BACnet device this point belongs to")

    def serialize_point_name(self) -> str:
        """Create a hierarchical point name including device context.

        Returns:
            Point name in format: device_path/object_type/object_index
        """
        return f"{self.device.serialize_device_path()}/{self.object_type}/{self.object_index}"

    def api_format(self) -> dict[str, Any]:
        """Format the point for API submission.

        Returns:
            Dictionary formatted for API compatibility
        """
        return {
            "name": self.serialize_point_name(),
            "site": self.device.site,
            "client": self.device.client,
            "point_type": "bacnet",
            "kv_tags": self.kv_tags,
            "collect_config": self.collect_config,
            "collect_enabled": self.collect_enabled,
            "collect_interval": self.collect_interval,
            "marker_tags": self.marker_tags,
            "bacnet_data": {
                "device_address": self.device.device_address,
                "device_id": int(self.device.device_id),
                "object_type": self.object_type,
                "object_index": int(self.object_index),
                "object_name": self.object_name,
                "object_units": self.object_units,
                "device_name": self.device.device_name,
                "device_description": self.device.device_description,
                "object_description": self.object_description,
                "present_value": self.present_value,
            },
        }

    @classmethod
    def from_api_model(cls, point: dict[str, Any]) -> BACnetPoint:
        """Create a BACnetPoint from API response data.

        Args:
            point: Dictionary containing point data from API

        Returns:
            BACnetPoint instance
        """
        bacnet_data = point.get("bacnet_data", {})

        # Extract raw properties (those starting with 'raw_')
        raw_properties = {
            key[4:]: value for key, value in bacnet_data.items() if key.startswith("raw_")
        }

        return cls(
            name=point["name"],
            point_type=point["point_type"],
            object_type=bacnet_data["object_type"],
            object_index=str(bacnet_data["object_index"]),  # Convert to string if needed
            object_units=bacnet_data.get("object_units"),
            object_name=bacnet_data["object_name"],
            object_description=bacnet_data.get("object_description", ""),
            present_value=bacnet_data["present_value"],
            marker_tags=point.get("marker_tags", []),
            kv_tags=point.get("kv_tags", {}),
            collect_config=point.get("collect_config", {}),
            raw_properties=raw_properties,
            device=BACnetDevice.from_api_point(point),
            created=datetime.fromisoformat(point["created"]) if "created" in point else None,
            updated=datetime.fromisoformat(point["updated"]) if "updated" in point else None,
            collect_enabled=point.get("collect_enabled", False),
            collect_interval=point.get("collect_interval", 300),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert BACnetPoint to dictionary for serialization.

        Returns:
            Dictionary representation of the point
        """
        return {
            "name": self.name,
            "point_type": self.point_type,
            "marker_tags": self.marker_tags,
            "kv_tags": self.kv_tags,
            "collect_config": self.collect_config,
            "object_type": self.object_type,
            "object_index": self.object_index,
            "object_units": self.object_units,
            "object_name": self.object_name,
            "object_description": self.object_description,
            "present_value": self.present_value,
            "raw_properties": self.raw_properties,
            "device": self.device.to_dict(),
            "created": self.created.isoformat().replace("+00:00", "Z") if self.created else None,
            "updated": self.updated.isoformat().replace("+00:00", "Z") if self.updated else None,
            "collect_enabled": self.collect_enabled,
            "collect_interval": self.collect_interval,
        }


class BACnetPointCreate(BACnetPointBase):
    """Model for creating a new BACnet point."""

    device_id: int = Field(..., description="ID of the BACnet device this point belongs to")


class BACnetPointUpdate(BaseModel):
    """Model for updating an existing BACnet point."""

    name: str | None = Field(None, description="Unique name for this point")
    marker_tags: list[str] | None = Field(None, description="List of marker tags")
    kv_tags: dict[str, str] | None = Field(None, description="Key-value tag pairs")
    collect_config: dict[str, Any] | None = Field(None, description="Collection configuration")
    object_units: str | None = Field(None, description="Engineering units for this object")
    object_description: str | None = Field(None, description="BACnet object description")
    present_value: str | None = Field(None, description="Current value of the BACnet object")
    raw_properties: dict[str, Any] | None = Field(None, description="Raw BACnet properties")
    collect_enabled: bool | None = Field(
        None, description="Whether collection is enabled for this point"
    )
    collect_interval: int | None = Field(None, description="Collection interval in seconds")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate name is non-empty if provided."""
        if v is None:
            return v
        return validate_non_empty_string(v, "name")

    @field_validator("collect_interval")
    @classmethod
    def validate_collect_interval(cls, v: int | None) -> int | None:
        """Validate collect_interval is positive if provided."""
        if v is None:
            return v
        if v <= 0:
            raise ValueError("collect_interval must be positive")
        return v


class BACnetPointResponse(BACnetPoint):
    """API response model for a BACnet point."""


class BACnetPointReference(BaseModel):
    """Minimal reference model for a BACnet point."""

    id: int = Field(..., description="Unique identifier for this point")
    name: str = Field(..., description="Unique name for this point")
    object_name: str = Field(..., description="BACnet object name")


__all__ = [
    "DEVICE_ADDRESS_NORMALIZE_MAP",
    "BACnetDevice",
    "BACnetDeviceBase",
    "BACnetDeviceCreate",
    "BACnetDeviceReference",
    "BACnetDeviceResponse",
    "BACnetDeviceUpdate",
    "BACnetPoint",
    "BACnetPointBase",
    "BACnetPointCreate",
    "BACnetPointReference",
    "BACnetPointResponse",
    "BACnetPointUpdate",
]
