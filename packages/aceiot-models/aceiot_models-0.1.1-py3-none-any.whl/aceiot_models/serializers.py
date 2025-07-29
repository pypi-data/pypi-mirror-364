"""Serialization and deserialization utilities for ACE IoT models."""

import base64
import json
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, TypeVar, cast

from pydantic import BaseModel, ValidationError

from .common import ErrorResponse, create_generic_error, create_validation_error


T = TypeVar("T", bound=BaseModel)


class SerializationError(Exception):
    """Custom exception for serialization errors."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


class DeserializationError(Exception):
    """Custom exception for deserialization errors."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


class ModelSerializer:
    """Universal serializer for Pydantic models."""

    @staticmethod
    def serialize_to_dict(
        model: BaseModel, exclude_none: bool = False, exclude_unset: bool = False
    ) -> dict[str, Any]:
        """Serialize Pydantic model to dictionary."""
        try:
            return model.model_dump(
                exclude_none=exclude_none,
                exclude_unset=exclude_unset,
                by_alias=True,
                serialize_as_any=True,
            )
        except Exception as e:
            raise SerializationError(f"Failed to serialize model to dict: {e!s}", e) from e

    @staticmethod
    def serialize_to_json(
        model: BaseModel,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        indent: int | None = None,
    ) -> str:
        """Serialize Pydantic model to JSON string."""
        try:
            data = ModelSerializer.serialize_to_dict(model, exclude_none, exclude_unset)
            return json.dumps(data, indent=indent, default=ModelSerializer._json_serializer)
        except Exception as e:
            raise SerializationError(f"Failed to serialize model to JSON: {e!s}", e) from e

    @staticmethod
    def deserialize_from_dict(model_class: type[T], data: dict[str, Any]) -> T:
        """Deserialize dictionary to Pydantic model."""
        try:
            return cast("T", model_class.model_validate(data))
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                error_messages.append(f"{field}: {message}")

            raise DeserializationError(
                f"Validation failed for {model_class.__name__}: {'; '.join(error_messages)}", e
            ) from e
        except Exception as e:
            raise DeserializationError(
                f"Failed to deserialize to {model_class.__name__}: {e!s}", e
            ) from e

    @staticmethod
    def deserialize_from_json(model_class: type[T], json_str: str) -> T:
        """Deserialize JSON string to Pydantic model."""
        try:
            data = json.loads(json_str)
            return ModelSerializer.deserialize_from_dict(model_class, data)
        except json.JSONDecodeError as e:
            raise DeserializationError(f"Invalid JSON format: {e!s}", e) from e

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """Custom JSON serializer for special types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class BulkSerializer:
    """Serializer for handling bulk operations with multiple models."""

    @staticmethod
    def serialize_list(
        models: Sequence[BaseModel], exclude_none: bool = False
    ) -> list[dict[str, Any]]:
        """Serialize list of models to list of dictionaries."""
        try:
            return [
                ModelSerializer.serialize_to_dict(model, exclude_none=exclude_none)
                for model in models
            ]
        except Exception as e:
            raise SerializationError(f"Failed to serialize model list: {e!s}", e) from e

    @staticmethod
    def deserialize_list(model_class: type[T], data_list: list[dict[str, Any]]) -> list[T]:
        """Deserialize list of dictionaries to list of models."""
        try:
            models = []
            errors = []

            for i, data in enumerate(data_list):
                try:
                    model = ModelSerializer.deserialize_from_dict(model_class, data)
                    models.append(model)
                except DeserializationError as e:
                    errors.append(f"Item {i}: {e!s}")

            if errors:
                raise DeserializationError(
                    f"Failed to deserialize some items: {'; '.join(errors[:5])}"
                )

            return models
        except Exception as e:
            raise DeserializationError(f"Failed to deserialize model list: {e!s}", e) from e


class HashSerializer:
    """Serializer for handling base64 and hex hash encodings."""

    @staticmethod
    def encode_hash_base64(hash_hex: str) -> str:
        """Convert hex hash to base64 encoding."""
        try:
            hash_bytes = bytes.fromhex(hash_hex)
            return base64.b64encode(hash_bytes).decode("ascii")
        except ValueError as e:
            raise SerializationError(f"Invalid hex hash format: {e!s}", e) from e

    @staticmethod
    def decode_hash_base64(hash_b64: str) -> str:
        """Convert base64 hash to hex encoding."""
        try:
            hash_bytes = base64.b64decode(hash_b64)
            return hash_bytes.hex()
        except Exception as e:
            raise DeserializationError(f"Invalid base64 hash format: {e!s}", e) from e

    @staticmethod
    def normalize_hash(hash_value: str, target_format: str = "hex") -> str:
        """Normalize hash to specified format (hex or base64)."""
        if not hash_value:
            return hash_value

        # Try to determine current format
        try:
            # Check if it's hex
            bytes.fromhex(hash_value)
            current_format = "hex"
        except ValueError:
            try:
                # Check if it's base64
                base64.b64decode(hash_value, validate=True)
                current_format = "base64"
            except Exception:
                raise SerializationError(f"Unknown hash format: {hash_value}") from None

        # Convert if needed
        if current_format == target_format:
            return hash_value
        elif current_format == "hex" and target_format == "base64":
            return HashSerializer.encode_hash_base64(hash_value)
        elif current_format == "base64" and target_format == "hex":
            return HashSerializer.decode_hash_base64(hash_value)
        else:
            raise SerializationError(
                f"Unsupported hash format conversion: {current_format} -> {target_format}"
            )


class DateTimeSerializer:
    """Serializer for handling datetime objects and timezone conversions."""

    @staticmethod
    def serialize_datetime(dt: datetime, iso_format: bool = True) -> str | None:
        """Serialize datetime to string."""
        if dt is None:
            return None

        try:
            if iso_format:
                return dt.isoformat()
            else:
                return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            raise SerializationError(f"Failed to serialize datetime: {e!s}", e) from e

    @staticmethod
    def deserialize_datetime(dt_str: str) -> datetime | None:
        """Deserialize string to datetime."""
        if not dt_str:
            return None

        try:
            # Try ISO format first
            if "T" in dt_str:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            else:
                # Try standard format
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            raise DeserializationError(f"Failed to parse datetime '{dt_str}': {e!s}", e) from e

    @staticmethod
    def ensure_utc(dt: datetime) -> datetime | None:
        """Ensure datetime is in UTC timezone."""
        if dt is None:
            return None

        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            return dt.replace(tzinfo=UTC)
        elif dt.tzinfo != UTC:
            # Convert to UTC
            return dt.astimezone(UTC)

        return dt


class ValidationSerializer:
    """Serializer with enhanced validation and error reporting."""

    @staticmethod
    def validate_and_serialize(model: BaseModel) -> dict[str, Any]:
        """Validate model and serialize with detailed error reporting."""
        try:
            # Re-validate the model to catch any issues
            model.model_validate(model.model_dump())
            return ModelSerializer.serialize_to_dict(model)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                errors.append(
                    {
                        "field": field,
                        "message": error["msg"],
                        "type": error["type"],
                        "input": error.get("input"),
                    }
                )

            raise SerializationError(f"Validation failed: {errors}") from e

    @staticmethod
    def safe_deserialize(model_class: type[T], data: dict[str, Any]) -> T | ErrorResponse:
        """Safely deserialize data, returning ErrorResponse on failure."""
        try:
            return ModelSerializer.deserialize_from_dict(model_class, data)
        except DeserializationError as e:
            return create_validation_error(
                field="unknown", message=str(e), code="deserialization_error"
            )
        except Exception as e:
            return create_generic_error(
                message=f"Unexpected error during deserialization: {e!s}", code="unexpected_error"
            )


class APIResponseSerializer:
    """Serializer specifically for API responses following swagger spec."""

    @staticmethod
    def serialize_paginated_response(
        items: Sequence[BaseModel], page: int, per_page: int, total: int
    ) -> dict[str, Any]:
        """Serialize paginated response according to API spec."""
        import math

        pages = math.ceil(total / per_page) if per_page > 0 else 1

        return {
            "page": page,
            "pages": pages,
            "per_page": per_page,
            "total": total,
            "items": [ModelSerializer.serialize_to_dict(item) for item in items],
        }

    @staticmethod
    def serialize_error_response(
        error: str, details: dict[str, Any] | None = None, code: str | None = None
    ) -> dict[str, Any]:
        """Serialize error response according to API spec."""
        response: dict[str, Any] = {"error": error, "timestamp": datetime.now(UTC).isoformat()}

        if details:
            response["details"] = details

        if code:
            response["code"] = code

        return response


# Utility functions
def auto_detect_model_type(data: dict[str, Any]) -> str | None:
    """Auto-detect model type based on data structure."""
    # This could be enhanced with more sophisticated detection logic
    if "client_id" in data and "site_id" in data and "name" in data:
        if "bacnet_data" in data or "marker_tags" in data:
            return "Point"
        else:
            return "Gateway"
    elif "nice_name" in data and "address" in data:
        if "vtron_ip" in data:
            return "Site"
        else:
            return "Client"
    elif "event_start" in data and "event_end" in data:
        return "DerEvent"
    elif "identity" in data and "package_name" in data:
        return "VolttronAgent"
    elif "content_blob" in data and "hawke_identity" in data:
        return "HawkeConfig"
    elif "email" in data:
        return "User"

    return None


def serialize_for_api(model: BaseModel, exclude_readonly: bool = True) -> dict[str, Any]:
    """Serialize model for API response, optionally excluding readonly fields."""
    data = ModelSerializer.serialize_to_dict(model, exclude_none=True)

    if exclude_readonly:
        # Remove readonly fields that shouldn't be in API responses
        readonly_fields = {"created", "updated", "id"}
        for field in readonly_fields:
            data.pop(field, None)

    return data


def deserialize_from_api[T: BaseModel](
    model_class: type[T], data: dict[str, Any], strict: bool = True
) -> T:
    """Deserialize data from API request with optional strict validation."""
    try:
        if strict:
            return ModelSerializer.deserialize_from_dict(model_class, data)
        else:
            # Filter out unknown fields for non-strict deserialization
            model_fields = set(model_class.model_fields.keys())
            filtered_data = {k: v for k, v in data.items() if k in model_fields}
            return ModelSerializer.deserialize_from_dict(model_class, filtered_data)
    except Exception as e:
        raise DeserializationError(f"Failed to deserialize from API data: {e!s}", e) from e


# Export all functionality
__all__ = [
    "APIResponseSerializer",
    "BulkSerializer",
    "DateTimeSerializer",
    "DeserializationError",
    "HashSerializer",
    "ModelSerializer",
    "SerializationError",
    "ValidationSerializer",
    "auto_detect_model_type",
    "deserialize_from_api",
    "serialize_for_api",
]
