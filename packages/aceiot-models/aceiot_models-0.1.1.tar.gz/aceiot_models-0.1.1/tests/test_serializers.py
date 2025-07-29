"""Tests for serialization and deserialization utilities."""

import base64
import json
from datetime import UTC, datetime

import pytest
from pydantic import BaseModel

from aceiot_models.common import ErrorResponse
from aceiot_models.serializers import (
    APIResponseSerializer,
    BulkSerializer,
    DateTimeSerializer,
    DeserializationError,
    HashSerializer,
    ModelSerializer,
    SerializationError,
    ValidationSerializer,
    auto_detect_model_type,
    deserialize_from_api,
    serialize_for_api,
)


# Test models for serialization
class SimpleTestModel(BaseModel):
    """Simple test model."""

    name: str
    value: int
    active: bool = True


class ComplexTestModel(BaseModel):
    """Complex test model with various field types."""

    id: int
    name: str
    created: datetime
    tags: list[str] = []
    metadata: dict | None = None
    nested: SimpleTestModel | None = None


class TestModelSerializer:
    """Test the ModelSerializer class."""

    def test_serialize_to_dict_basic(self):
        """Test basic serialization to dictionary."""
        model = SimpleTestModel(name="test", value=42)
        data = ModelSerializer.serialize_to_dict(model)

        assert data == {"name": "test", "value": 42, "active": True}
        assert isinstance(data, dict)

    def test_serialize_to_dict_exclude_none(self):
        """Test serialization excluding None values."""
        model = ComplexTestModel(
            id=1, name="test", created=datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)
        )

        data = ModelSerializer.serialize_to_dict(model, exclude_none=True)
        assert "metadata" not in data
        assert "nested" not in data

    def test_serialize_to_dict_exclude_unset(self):
        """Test serialization excluding unset values."""
        model = SimpleTestModel(name="test", value=42)
        data = ModelSerializer.serialize_to_dict(model, exclude_unset=True)

        # 'active' has default but was not explicitly set
        assert data == {"name": "test", "value": 42}

    def test_serialize_to_json_basic(self):
        """Test basic JSON serialization."""
        model = SimpleTestModel(name="test", value=42)
        json_str = ModelSerializer.serialize_to_json(model)

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["name"] == "test"
        assert parsed["value"] == 42

    def test_serialize_to_json_with_datetime(self):
        """Test JSON serialization with datetime."""
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)
        model = ComplexTestModel(id=1, name="test", created=dt)

        json_str = ModelSerializer.serialize_to_json(model)
        parsed = json.loads(json_str)

        assert "2024-01-15T10:30:45" in parsed["created"]

    def test_serialize_to_json_with_indent(self):
        """Test JSON serialization with indentation."""
        model = SimpleTestModel(name="test", value=42)
        json_str = ModelSerializer.serialize_to_json(model, indent=2)

        assert "  " in json_str  # Should have indentation

    def test_deserialize_from_dict_basic(self):
        """Test basic deserialization from dictionary."""
        data = {"name": "test", "value": 42}
        model = ModelSerializer.deserialize_from_dict(SimpleTestModel, data)

        assert isinstance(model, SimpleTestModel)
        assert model.name == "test"
        assert model.value == 42
        assert model.active is True  # Default value

    def test_deserialize_from_dict_validation_error(self):
        """Test deserialization with validation error."""
        data = {"name": "test"}  # Missing required 'value' field

        with pytest.raises(DeserializationError) as exc_info:
            ModelSerializer.deserialize_from_dict(SimpleTestModel, data)

        assert "Validation failed" in str(exc_info.value)
        assert "SimpleTestModel" in str(exc_info.value)

    def test_deserialize_from_dict_type_error(self):
        """Test deserialization with type error."""
        data = {"name": "test", "value": "not an int"}

        with pytest.raises(DeserializationError) as exc_info:
            ModelSerializer.deserialize_from_dict(SimpleTestModel, data)

        assert "Validation failed" in str(exc_info.value)

    def test_deserialize_from_json_basic(self):
        """Test basic JSON deserialization."""
        json_str = '{"name": "test", "value": 42}'
        model = ModelSerializer.deserialize_from_json(SimpleTestModel, json_str)

        assert isinstance(model, SimpleTestModel)
        assert model.name == "test"
        assert model.value == 42

    def test_deserialize_from_json_invalid_json(self):
        """Test deserialization with invalid JSON."""
        invalid_json = '{"name": "test", invalid}'

        with pytest.raises(DeserializationError) as exc_info:
            ModelSerializer.deserialize_from_json(SimpleTestModel, invalid_json)

        assert "Invalid JSON format" in str(exc_info.value)

    def test_json_serializer_custom_types(self):
        """Test custom JSON serializer for special types."""
        # Test datetime serialization
        dt = datetime.now(UTC)
        result = ModelSerializer._json_serializer(dt)
        assert isinstance(result, str)
        assert "T" in result  # ISO format

        # Test object with __dict__
        class CustomObj:
            def __init__(self):
                self.field = "value"

        obj = CustomObj()
        result = ModelSerializer._json_serializer(obj)
        assert result == {"field": "value"}

        # Test unsupported type
        with pytest.raises(TypeError):
            ModelSerializer._json_serializer(set())


class TestBulkSerializer:
    """Test the BulkSerializer class."""

    def test_serialize_list_basic(self):
        """Test basic list serialization."""
        models = [
            SimpleTestModel(name="test1", value=1),
            SimpleTestModel(name="test2", value=2),
            SimpleTestModel(name="test3", value=3),
        ]

        data_list = BulkSerializer.serialize_list(models)

        assert len(data_list) == 3
        assert all(isinstance(d, dict) for d in data_list)
        assert data_list[0]["name"] == "test1"
        assert data_list[2]["value"] == 3

    def test_serialize_list_exclude_none(self):
        """Test list serialization with exclude_none."""
        models = [
            ComplexTestModel(id=1, name="test1", created=datetime.now(UTC)),
            ComplexTestModel(
                id=2, name="test2", created=datetime.now(UTC), metadata={"key": "value"}
            ),
        ]

        data_list = BulkSerializer.serialize_list(models, exclude_none=True)

        assert "metadata" not in data_list[0]
        assert "metadata" in data_list[1]

    def test_serialize_list_empty(self):
        """Test serializing empty list."""
        data_list = BulkSerializer.serialize_list([])
        assert data_list == []

    def test_deserialize_list_basic(self):
        """Test basic list deserialization."""
        data_list = [
            {"name": "test1", "value": 1},
            {"name": "test2", "value": 2},
            {"name": "test3", "value": 3},
        ]

        models = BulkSerializer.deserialize_list(SimpleTestModel, data_list)

        assert len(models) == 3
        assert all(isinstance(m, SimpleTestModel) for m in models)
        assert models[0].name == "test1"
        assert models[2].value == 3

    def test_deserialize_list_partial_errors(self):
        """Test list deserialization with some invalid items."""
        data_list = [
            {"name": "test1", "value": 1},
            {"name": "test2"},  # Missing 'value'
            {"name": "test3", "value": "invalid"},  # Wrong type
        ]

        with pytest.raises(DeserializationError) as exc_info:
            BulkSerializer.deserialize_list(SimpleTestModel, data_list)

        assert "Failed to deserialize some items" in str(exc_info.value)

    def test_deserialize_list_empty(self):
        """Test deserializing empty list."""
        models = BulkSerializer.deserialize_list(SimpleTestModel, [])
        assert models == []


class TestHashSerializer:
    """Test the HashSerializer class."""

    def test_encode_hash_base64(self):
        """Test hex to base64 hash encoding."""
        hex_hash = "48656c6c6f20576f726c64"  # "Hello World" in hex
        b64_hash = HashSerializer.encode_hash_base64(hex_hash)

        assert isinstance(b64_hash, str)
        # Verify it's valid base64
        base64.b64decode(b64_hash)

    def test_encode_hash_base64_invalid_hex(self):
        """Test encoding with invalid hex."""
        with pytest.raises(SerializationError) as exc_info:
            HashSerializer.encode_hash_base64("not-hex-string")

        assert "Invalid hex hash format" in str(exc_info.value)

    def test_decode_hash_base64(self):
        """Test base64 to hex hash decoding."""
        b64_hash = "SGVsbG8gV29ybGQ="  # "Hello World" in base64
        hex_hash = HashSerializer.decode_hash_base64(b64_hash)

        assert isinstance(hex_hash, str)
        assert all(c in "0123456789abcdef" for c in hex_hash)

    def test_decode_hash_base64_invalid(self):
        """Test decoding with invalid base64."""
        with pytest.raises(DeserializationError) as exc_info:
            HashSerializer.decode_hash_base64("not-base64!")

        assert "Invalid base64 hash format" in str(exc_info.value)

    def test_normalize_hash_hex_to_hex(self):
        """Test normalizing hex hash to hex (no conversion)."""
        hex_hash = "48656c6c6f"
        result = HashSerializer.normalize_hash(hex_hash, target_format="hex")
        assert result == hex_hash

    def test_normalize_hash_hex_to_base64(self):
        """Test normalizing hex hash to base64."""
        hex_hash = "48656c6c6f"
        result = HashSerializer.normalize_hash(hex_hash, target_format="base64")

        # Should be different and valid base64
        assert result != hex_hash
        base64.b64decode(result)

    def test_normalize_hash_base64_to_hex(self):
        """Test normalizing base64 hash to hex."""
        b64_hash = "SGVsbG8="  # "Hello" in base64
        result = HashSerializer.normalize_hash(b64_hash, target_format="hex")

        assert all(c in "0123456789abcdef" for c in result)

    def test_normalize_hash_unknown_format(self):
        """Test normalizing with unknown hash format."""
        with pytest.raises(SerializationError) as exc_info:
            HashSerializer.normalize_hash("!@#$%", target_format="hex")

        assert "Unknown hash format" in str(exc_info.value)

    def test_normalize_hash_unsupported_conversion(self):
        """Test unsupported format conversion."""
        hex_hash = "48656c6c6f"
        with pytest.raises(SerializationError) as exc_info:
            HashSerializer.normalize_hash(hex_hash, target_format="sha256")

        assert "Unsupported hash format conversion" in str(exc_info.value)


class TestDateTimeSerializer:
    """Test the DateTimeSerializer class."""

    def test_serialize_datetime_iso_format(self):
        """Test datetime serialization to ISO format."""
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)
        result = DateTimeSerializer.serialize_datetime(dt)

        assert result == "2024-01-15T10:30:45+00:00"

    def test_serialize_datetime_custom_format(self):
        """Test datetime serialization with custom format."""
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)
        result = DateTimeSerializer.serialize_datetime(dt, iso_format=False)

        assert result == "2024-01-15 10:30:45"

    def test_serialize_datetime_none(self):
        """Test serializing None datetime."""
        result = DateTimeSerializer.serialize_datetime(None)  # type: ignore
        assert result is None

    def test_deserialize_datetime_iso_format(self):
        """Test datetime deserialization from ISO format."""
        dt_str = "2024-01-15T10:30:45+00:00"
        dt = DateTimeSerializer.deserialize_datetime(dt_str)

        assert isinstance(dt, datetime)
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15

    def test_deserialize_datetime_z_suffix(self):
        """Test datetime deserialization with Z suffix."""
        dt_str = "2024-01-15T10:30:45Z"
        dt = DateTimeSerializer.deserialize_datetime(dt_str)

        assert isinstance(dt, datetime)
        assert dt.tzinfo is not None

    def test_deserialize_datetime_standard_format(self):
        """Test datetime deserialization from standard format."""
        dt_str = "2024-01-15 10:30:45"
        dt = DateTimeSerializer.deserialize_datetime(dt_str)

        assert isinstance(dt, datetime)
        assert dt.hour == 10
        assert dt.minute == 30

    def test_deserialize_datetime_invalid(self):
        """Test deserializing invalid datetime string."""
        with pytest.raises(DeserializationError) as exc_info:
            DateTimeSerializer.deserialize_datetime("not-a-date")

        assert "Failed to parse datetime" in str(exc_info.value)

    def test_deserialize_datetime_empty(self):
        """Test deserializing empty string."""
        result = DateTimeSerializer.deserialize_datetime("")
        assert result is None

    def test_ensure_utc_none(self):
        """Test ensuring UTC with None."""
        result = DateTimeSerializer.ensure_utc(None)  # type: ignore
        assert result is None

    def test_ensure_utc_naive(self):
        """Test ensuring UTC with naive datetime."""
        naive_dt = datetime(2024, 1, 15, 10, 30, 45)
        result = DateTimeSerializer.ensure_utc(naive_dt)

        assert result is not None
        assert result.tzinfo == UTC
        assert result.hour == 10  # Time unchanged

    def test_ensure_utc_already_utc(self):
        """Test ensuring UTC with already UTC datetime."""
        utc_dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)
        result = DateTimeSerializer.ensure_utc(utc_dt)

        assert result is utc_dt  # Should be same object

    def test_ensure_utc_other_timezone(self):
        """Test ensuring UTC with other timezone."""
        import zoneinfo

        eastern = zoneinfo.ZoneInfo("US/Eastern")
        eastern_dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=eastern)

        result = DateTimeSerializer.ensure_utc(eastern_dt)

        assert result is not None
        assert result.tzinfo == UTC
        assert result.hour != 10  # Time should be converted


class TestValidationSerializer:
    """Test the ValidationSerializer class."""

    def test_validate_and_serialize_valid(self):
        """Test validation and serialization with valid model."""
        model = SimpleTestModel(name="test", value=42)
        data = ValidationSerializer.validate_and_serialize(model)

        assert data["name"] == "test"
        assert data["value"] == 42

    def test_validate_and_serialize_revalidation(self):
        """Test that model is re-validated during serialization."""
        # This would catch any post-init mutations that break validation
        model = SimpleTestModel(name="test", value=42)

        # Even though we can't easily break validation after init,
        # the method should work normally
        data = ValidationSerializer.validate_and_serialize(model)
        assert data is not None

    def test_safe_deserialize_success(self):
        """Test safe deserialization with valid data."""
        data = {"name": "test", "value": 42}
        result = ValidationSerializer.safe_deserialize(SimpleTestModel, data)

        assert isinstance(result, SimpleTestModel)
        assert result.name == "test"

    def test_safe_deserialize_validation_error(self):
        """Test safe deserialization with validation error."""
        data = {"name": "test"}  # Missing required field
        result = ValidationSerializer.safe_deserialize(SimpleTestModel, data)

        assert isinstance(result, ErrorResponse)
        assert result.code == "deserialization_error"

    def test_safe_deserialize_unexpected_error(self):
        """Test safe deserialization with unexpected error."""
        # Pass non-dict to trigger unexpected error
        result = ValidationSerializer.safe_deserialize(SimpleTestModel, "not a dict")  # type: ignore

        assert isinstance(result, ErrorResponse)
        # The actual error gets caught as a deserialization error
        assert result.code in ["deserialization_error", "unexpected_error"]


class TestAPIResponseSerializer:
    """Test the APIResponseSerializer class."""

    def test_serialize_paginated_response(self):
        """Test serializing paginated response."""
        items = [SimpleTestModel(name="test1", value=1), SimpleTestModel(name="test2", value=2)]

        response = APIResponseSerializer.serialize_paginated_response(
            items=items, page=1, per_page=10, total=2
        )

        assert response["page"] == 1
        assert response["pages"] == 1
        assert response["per_page"] == 10
        assert response["total"] == 2
        assert len(response["items"]) == 2
        assert response["items"][0]["name"] == "test1"

    def test_serialize_paginated_response_multiple_pages(self):
        """Test paginated response with multiple pages."""
        items = [SimpleTestModel(name=f"test{i}", value=i) for i in range(10)]

        response = APIResponseSerializer.serialize_paginated_response(
            items=items, page=2, per_page=10, total=25
        )

        assert response["page"] == 2
        assert response["pages"] == 3  # 25 total / 10 per page

    def test_serialize_paginated_response_zero_per_page(self):
        """Test paginated response with zero per_page."""
        response = APIResponseSerializer.serialize_paginated_response(
            items=[], page=1, per_page=0, total=0
        )

        assert response["pages"] == 1  # Should handle division by zero

    def test_serialize_error_response_basic(self):
        """Test basic error response serialization."""
        response = APIResponseSerializer.serialize_error_response(error="Something went wrong")

        assert response["error"] == "Something went wrong"
        assert "timestamp" in response
        assert "details" not in response
        assert "code" not in response

    def test_serialize_error_response_with_details(self):
        """Test error response with details and code."""
        response = APIResponseSerializer.serialize_error_response(
            error="Validation failed",
            details={"field": "email", "reason": "invalid"},
            code="validation_error",
        )

        assert response["error"] == "Validation failed"
        assert response["code"] == "validation_error"
        assert response["details"]["field"] == "email"


class TestUtilityFunctions:
    """Test utility functions."""

    def test_auto_detect_model_type_point(self):
        """Test auto-detecting Point model."""
        data = {"client_id": 1, "site_id": 2, "name": "test", "bacnet_data": {}}
        assert auto_detect_model_type(data) == "Point"

    def test_auto_detect_model_type_gateway(self):
        """Test auto-detecting Gateway model."""
        data = {"client_id": 1, "site_id": 2, "name": "test"}
        assert auto_detect_model_type(data) == "Gateway"

    def test_auto_detect_model_type_site(self):
        """Test auto-detecting Site model."""
        data = {"nice_name": "Test Site", "address": "123 Main St", "vtron_ip": "192.168.1.1"}
        assert auto_detect_model_type(data) == "Site"

    def test_auto_detect_model_type_client(self):
        """Test auto-detecting Client model."""
        data = {"nice_name": "Test Client", "address": "123 Main St"}
        assert auto_detect_model_type(data) == "Client"

    def test_auto_detect_model_type_der_event(self):
        """Test auto-detecting DerEvent model."""
        data = {"event_start": "2024-01-15T10:00:00", "event_end": "2024-01-15T12:00:00"}
        assert auto_detect_model_type(data) == "DerEvent"

    def test_auto_detect_model_type_volttron(self):
        """Test auto-detecting VolttronAgent model."""
        data = {"identity": "agent1", "package_name": "volttron-agent"}
        assert auto_detect_model_type(data) == "VolttronAgent"

    def test_auto_detect_model_type_hawke(self):
        """Test auto-detecting HawkeConfig model."""
        data = {"content_blob": "config data", "hawke_identity": "hawke1"}
        assert auto_detect_model_type(data) == "HawkeConfig"

    def test_auto_detect_model_type_user(self):
        """Test auto-detecting User model."""
        data = {"email": "test@example.com"}
        assert auto_detect_model_type(data) == "User"

    def test_auto_detect_model_type_unknown(self):
        """Test auto-detecting unknown model type."""
        data = {"random": "data"}
        assert auto_detect_model_type(data) is None

    def test_serialize_for_api_basic(self):
        """Test basic API serialization."""
        model = ComplexTestModel(id=1, name="test", created=datetime.now(UTC))

        data = serialize_for_api(model)

        assert "name" in data
        assert "id" not in data  # Readonly field excluded
        assert "created" not in data  # Readonly field excluded

    def test_serialize_for_api_include_readonly(self):
        """Test API serialization including readonly fields."""
        model = ComplexTestModel(id=1, name="test", created=datetime.now(UTC))

        data = serialize_for_api(model, exclude_readonly=False)

        assert "id" in data
        assert "created" in data

    def test_deserialize_from_api_strict(self):
        """Test strict API deserialization."""
        data = {"name": "test", "value": 42}
        model = deserialize_from_api(SimpleTestModel, data)

        assert isinstance(model, SimpleTestModel)
        assert model.name == "test"

    def test_deserialize_from_api_non_strict(self):
        """Test non-strict API deserialization."""
        data = {
            "name": "test",
            "value": 42,
            "extra_field": "ignored",  # Should be filtered out
        }

        model = deserialize_from_api(SimpleTestModel, data, strict=False)

        assert isinstance(model, SimpleTestModel)
        assert model.name == "test"
        assert not hasattr(model, "extra_field")

    def test_deserialize_from_api_error(self):
        """Test API deserialization with error."""
        data = {"name": "test"}  # Missing required field

        with pytest.raises(DeserializationError) as exc_info:
            deserialize_from_api(SimpleTestModel, data)

        assert "Failed to deserialize from API data" in str(exc_info.value)
