"""Tests for sample models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from aceiot_models.sample import (
    Sample,
    SampleBase,
    SampleCreate,
    SampleList,
    SampleResponse,
    SampleUpdate,
)


@pytest.fixture
def sample_sample_data(sample_datetime):
    """Sample data for creating a Sample."""
    return {
        "name": "temperature_sensor_1",
        "time": sample_datetime,
        "value": 23.5,
    }


@pytest.fixture
def sample_sample_api_data():
    """Sample API response data for a Sample."""
    return {
        "name": "temperature_sensor_1",
        "time": "2024-01-01T00:00:00Z",
        "value": 23.5,
    }


class TestSampleBase:
    """Tests for SampleBase model."""

    def test_sample_base_creation_valid(self, sample_sample_data):
        """Test creating a valid SampleBase."""
        sample = SampleBase(**sample_sample_data)
        assert sample.name == sample_sample_data["name"]
        assert sample.time == sample_sample_data["time"]
        assert sample.value == sample_sample_data["value"]

    def test_name_validation_empty(self, sample_sample_data):
        """Test that empty name is rejected."""
        sample_sample_data["name"] = ""
        with pytest.raises(ValidationError) as exc_info:
            SampleBase(**sample_sample_data)

        errors = exc_info.value.errors()
        assert any("name cannot be empty" in error["msg"] for error in errors)

    def test_name_validation_whitespace(self, sample_sample_data):
        """Test that whitespace-only name is rejected."""
        sample_sample_data["name"] = "   "
        with pytest.raises(ValidationError) as exc_info:
            SampleBase(**sample_sample_data)

        errors = exc_info.value.errors()
        assert any("name cannot be empty" in error["msg"] for error in errors)

    def test_name_stripping(self, sample_sample_data):
        """Test that name is stripped of whitespace."""
        sample_sample_data["name"] = "  sensor_name  "
        sample = SampleBase(**sample_sample_data)
        assert sample.name == "sensor_name"

    def test_value_validation_types(self, sample_sample_data):
        """Test value accepts different numeric types."""
        # Test integer
        sample_sample_data["value"] = 42
        sample = SampleBase(**sample_sample_data)
        assert sample.value == 42.0
        assert isinstance(sample.value, float)

        # Test float
        sample_sample_data["value"] = 42.5
        sample = SampleBase(**sample_sample_data)
        assert sample.value == 42.5

        # Test negative
        sample_sample_data["value"] = -10.5
        sample = SampleBase(**sample_sample_data)
        assert sample.value == -10.5

        # Test zero
        sample_sample_data["value"] = 0
        sample = SampleBase(**sample_sample_data)
        assert sample.value == 0.0

    def test_value_validation_invalid(self, sample_sample_data):
        """Test that invalid value types are rejected."""
        sample_sample_data["value"] = "not a number"
        with pytest.raises(ValidationError) as exc_info:
            SampleBase(**sample_sample_data)

        errors = exc_info.value.errors()
        assert any("Input should be a valid number" in error["msg"] for error in errors)

    def test_time_validation(self, sample_sample_data):
        """Test time field validation."""
        # Test with string ISO format
        sample_sample_data["time"] = "2024-01-01T12:30:00Z"
        sample = SampleBase(**sample_sample_data)
        assert isinstance(sample.time, datetime)
        assert sample.time.year == 2024

        # Test with invalid format
        sample_sample_data["time"] = "not a date"
        with pytest.raises(ValidationError) as exc_info:
            SampleBase(**sample_sample_data)

        errors = exc_info.value.errors()
        assert any("datetime" in error["type"] for error in errors)


class TestSample:
    """Tests for Sample model."""

    def test_sample_creation_valid(self, sample_sample_data):
        """Test creating a valid Sample."""
        sample = Sample(**sample_sample_data)
        assert sample.name == sample_sample_data["name"]
        assert sample.time == sample_sample_data["time"]
        assert sample.value == sample_sample_data["value"]

    def test_from_api_model(self, sample_sample_api_data):
        """Test creating Sample from API response data."""
        sample = Sample.from_api_model(sample_sample_api_data)
        assert sample.name == sample_sample_api_data["name"]
        assert sample.value == sample_sample_api_data["value"]
        assert isinstance(sample.time, datetime)
        assert sample.time.year == 2024
        assert sample.time.month == 1
        assert sample.time.day == 1

    def test_to_dict(self, sample_sample_data):
        """Test converting Sample to dictionary."""
        sample = Sample(**sample_sample_data)
        data = sample.to_dict()

        assert data["name"] == sample_sample_data["name"]
        assert data["value"] == sample_sample_data["value"]
        assert "time" in data
        assert isinstance(data["time"], str)
        assert data["time"].endswith("Z")

    def test_to_dict_timezone_handling(self):
        """Test that to_dict correctly handles UTC timezone."""
        sample = Sample(
            name="test", time=datetime.fromisoformat("2024-01-01T12:00:00+00:00"), value=10.0
        )
        data = sample.to_dict()
        assert data["time"] == "2024-01-01T12:00:00Z"

    def test_model_dump(self, sample_sample_data):
        """Test model_dump method."""
        sample = Sample(**sample_sample_data)
        data = sample.model_dump()

        assert data["name"] == sample_sample_data["name"]
        assert data["value"] == sample_sample_data["value"]
        # model_dump() returns ISO string for datetimes
        assert isinstance(data["time"], str)
        assert data["time"].endswith("+00:00")


class TestSampleCreate:
    """Tests for SampleCreate model."""

    def test_sample_create_valid(self, sample_sample_data):
        """Test creating a valid SampleCreate."""
        sample = SampleCreate(**sample_sample_data)
        assert sample.name == sample_sample_data["name"]
        assert sample.time == sample_sample_data["time"]
        assert sample.value == sample_sample_data["value"]

    def test_sample_create_inherits_validation(self, sample_sample_data):
        """Test that SampleCreate inherits validation from SampleBase."""
        sample_sample_data["name"] = ""
        with pytest.raises(ValidationError) as exc_info:
            SampleCreate(**sample_sample_data)

        errors = exc_info.value.errors()
        assert any("name cannot be empty" in error["msg"] for error in errors)


class TestSampleUpdate:
    """Tests for SampleUpdate model."""

    def test_sample_update_all_fields(self, sample_sample_data):
        """Test updating all fields."""
        update = SampleUpdate(**sample_sample_data)
        assert update.name == sample_sample_data["name"]
        assert update.time == sample_sample_data["time"]
        assert update.value == sample_sample_data["value"]

    def test_sample_update_optional_fields(self):
        """Test that all fields are optional in update."""
        # Empty update
        update = SampleUpdate()
        assert update.name is None
        assert update.time is None
        assert update.value is None

        # Partial update
        update = SampleUpdate(name="new_name")
        assert update.name == "new_name"
        assert update.time is None
        assert update.value is None

    def test_sample_update_validation(self):
        """Test that validation still applies for provided fields."""
        # Empty name should fail
        with pytest.raises(ValidationError) as exc_info:
            SampleUpdate(name="")

        errors = exc_info.value.errors()
        assert any("name cannot be empty" in error["msg"] for error in errors)

        # Invalid value type should fail
        with pytest.raises(ValidationError) as exc_info:
            SampleUpdate(value="not a number")

        errors = exc_info.value.errors()
        assert any("Input should be a valid number" in error["msg"] for error in errors)

    def test_sample_update_none_values(self):
        """Test that None values are preserved."""
        update = SampleUpdate(name=None, time=None, value=None)
        assert update.name is None
        assert update.time is None
        assert update.value is None


class TestSampleResponse:
    """Tests for SampleResponse model."""

    def test_sample_response_creation(self, sample_sample_data):
        """Test creating a SampleResponse."""
        response = SampleResponse(**sample_sample_data)
        assert response.name == sample_sample_data["name"]
        assert response.time == sample_sample_data["time"]
        assert response.value == sample_sample_data["value"]

    def test_sample_response_inherits_from_sample(self, sample_sample_data):
        """Test that SampleResponse inherits from Sample."""
        response = SampleResponse(**sample_sample_data)
        assert isinstance(response, Sample)

        # Should have all Sample methods
        data = response.to_dict()
        assert "name" in data
        assert "time" in data
        assert "value" in data


class TestSampleList:
    """Tests for SampleList model."""

    def test_sample_list_empty(self):
        """Test creating an empty SampleList."""
        sample_list = SampleList(samples=[], count=0)
        assert sample_list.samples == []
        assert sample_list.count == 0

    def test_sample_list_with_samples(self, sample_sample_data):
        """Test creating SampleList with samples."""
        sample1 = Sample(**sample_sample_data)
        sample2 = Sample(name="sensor_2", time=sample_sample_data["time"], value=25.0)

        sample_list = SampleList(samples=[sample1, sample2], count=2)
        assert len(sample_list.samples) == 2
        assert sample_list.count == 2
        assert sample_list.samples[0].name == "temperature_sensor_1"
        assert sample_list.samples[1].name == "sensor_2"

    def test_sample_list_defaults(self):
        """Test SampleList with default values."""
        sample_list = SampleList(count=0)
        assert sample_list.samples == []
        assert sample_list.count == 0

    def test_sample_list_validation(self, sample_sample_data):
        """Test SampleList validation."""
        # Count is required
        with pytest.raises(ValidationError):
            SampleList(samples=[])

        # Samples must be valid Sample objects
        with pytest.raises(ValidationError):
            SampleList(samples=[{"invalid": "data"}], count=1)
