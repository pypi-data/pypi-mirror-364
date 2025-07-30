"""Tests for timeseries models."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from aceiot_models.timeseries import (
    AggregatedPointSample,
    BulkTimeseriesData,
    PointSample,
    TimeseriesData,
    TimeseriesMetadata,
    TimeseriesQuery,
    TimeseriesResponse,
    WeatherData,
    WeatherPointSample,
    calculate_sampling_statistics,
    create_point_sample,
    filter_samples_by_time_range,
    group_samples_by_point,
    resample_timeseries,
    validate_timeseries_data_quality,
)


class TestPointSample:
    """Test the PointSample model."""

    def test_point_sample_creation_valid(self, sample_point_sample_data):
        """Test creating a valid PointSample."""
        sample = PointSample(
            name=sample_point_sample_data["name"],
            value=sample_point_sample_data["value"],
            time=sample_point_sample_data["time"],
        )

        assert sample.name == sample_point_sample_data["name"]
        assert sample.value == sample_point_sample_data["value"]
        assert isinstance(sample.time, datetime)

    def test_point_sample_with_different_value_types(self, sample_datetime):
        """Test PointSample with different value types."""
        # String value
        sample_str = PointSample(name="test", value="string_value", time=sample_datetime)
        assert sample_str.value == "string_value"

        # Integer value
        sample_int = PointSample(name="test", value=42, time=sample_datetime)
        assert sample_int.value == 42

        # Float value
        sample_float = PointSample(name="test", value=3.14, time=sample_datetime)
        assert sample_float.value == 3.14

        # Boolean value
        sample_bool = PointSample(name="test", value=True, time=sample_datetime)
        assert sample_bool.value is True

        # None value
        sample_none = PointSample(name="test", value=None, time=sample_datetime)
        assert sample_none.value is None

    def test_point_sample_name_validation(self, sample_datetime):
        """Test name validation in PointSample."""
        # Test empty name
        with pytest.raises(ValidationError) as exc_info:
            PointSample(name="", value="test", time=sample_datetime)

        errors = exc_info.value.errors()
        assert any("Point name cannot be empty" in error["msg"] for error in errors)

        # Test name with only whitespace
        with pytest.raises(ValidationError) as exc_info:
            PointSample(name="   ", value="test", time=sample_datetime)

        errors = exc_info.value.errors()
        assert any("Point name cannot be empty" in error["msg"] for error in errors)

    def test_point_sample_name_stripping(self, sample_datetime):
        """Test that point names are stripped of whitespace."""
        sample = PointSample(name="  test_name  ", value="test", time=sample_datetime)
        assert sample.name == "test_name"

    def test_point_sample_time_validation(self):
        """Test time validation in PointSample."""
        # Test None time
        with pytest.raises(ValidationError) as exc_info:
            PointSample(name="test", value="test", time=None)  # type: ignore

        errors = exc_info.value.errors()
        # Check that the validation error is for 'time' field
        assert any(error["loc"] == ("time",) for error in errors)

    def test_point_sample_time_validation_direct(self):
        """Test direct validator for edge case coverage."""
        # This tests the validator directly for code coverage
        from aceiot_models.timeseries import PointSample

        # Test that the validator returns the datetime when it's not None
        test_time = datetime.now(UTC)
        assert PointSample.validate_time_not_none(test_time) == test_time

    def test_point_sample_model_dump(self, sample_point_sample_data):
        """Test model serialization."""
        sample = PointSample(**sample_point_sample_data)
        data = sample.model_dump()

        assert data["name"] == sample_point_sample_data["name"]
        assert data["value"] == sample_point_sample_data["value"]
        # When dumping, datetime is serialized to string by default
        assert isinstance(data["time"], str)


class TestTimeseriesData:
    """Test the TimeseriesData model."""

    def test_timeseries_data_creation_valid(self, sample_timeseries_data):
        """Test creating a valid TimeseriesData."""
        ts_data = TimeseriesData(**sample_timeseries_data)

        assert len(ts_data.point_samples) == 2
        assert all(isinstance(sample, PointSample) for sample in ts_data.point_samples)

    def test_timeseries_data_empty_validation(self):
        """Test validation for empty point samples."""
        with pytest.raises(ValidationError) as exc_info:
            TimeseriesData(point_samples=[])

        errors = exc_info.value.errors()
        assert any("Point samples list cannot be empty" in error["msg"] for error in errors)

    def test_timeseries_data_single_sample(self, sample_point_sample_data):
        """Test TimeseriesData with a single sample."""
        ts_data = TimeseriesData(point_samples=[PointSample(**sample_point_sample_data)])
        assert len(ts_data.point_samples) == 1


class TestTimeseriesQuery:
    """Test the TimeseriesQuery model."""

    def test_timeseries_query_creation_valid(self, sample_datetime):
        """Test creating a valid TimeseriesQuery."""
        start_time = sample_datetime
        end_time = start_time + timedelta(hours=1)

        query = TimeseriesQuery(
            point_names=["temp_sensor_1", "humidity_sensor_1"],
            start_time=start_time,
            end_time=end_time,
        )

        assert len(query.point_names) == 2
        assert query.start_time == start_time
        assert query.end_time == end_time

    def test_timeseries_query_empty_point_names(self, sample_datetime):
        """Test validation for empty point names."""
        with pytest.raises(ValidationError) as exc_info:
            TimeseriesQuery(
                point_names=[],
                start_time=sample_datetime,
                end_time=sample_datetime + timedelta(hours=1),
            )

        errors = exc_info.value.errors()
        assert any("At least one point name must be provided" in error["msg"] for error in errors)

    def test_timeseries_query_invalid_point_names(self, sample_datetime):
        """Test validation for invalid point names."""
        # Test with empty string
        with pytest.raises(ValidationError) as exc_info:
            TimeseriesQuery(
                point_names=["valid_name", ""],
                start_time=sample_datetime,
                end_time=sample_datetime + timedelta(hours=1),
            )

        errors = exc_info.value.errors()
        assert any("All point names must be non-empty strings" in error["msg"] for error in errors)

        # Test with whitespace only
        with pytest.raises(ValidationError) as exc_info:
            TimeseriesQuery(
                point_names=["valid_name", "   "],
                start_time=sample_datetime,
                end_time=sample_datetime + timedelta(hours=1),
            )

        errors = exc_info.value.errors()
        assert any("All point names must be non-empty strings" in error["msg"] for error in errors)

    def test_timeseries_query_name_stripping(self, sample_datetime):
        """Test that point names are stripped."""
        query = TimeseriesQuery(
            point_names=["  sensor_1  ", "  sensor_2  "],
            start_time=sample_datetime,
            end_time=sample_datetime + timedelta(hours=1),
        )

        assert query.point_names == ["sensor_1", "sensor_2"]

    def test_timeseries_query_time_validation(self, sample_datetime):
        """Test time range validation."""
        # Test end time before start time
        with pytest.raises(ValidationError) as exc_info:
            TimeseriesQuery(
                point_names=["sensor_1"],
                start_time=sample_datetime,
                end_time=sample_datetime - timedelta(hours=1),
            )

        errors = exc_info.value.errors()
        assert any("End time must be after start time" in error["msg"] for error in errors)

        # Test end time equal to start time
        with pytest.raises(ValidationError) as exc_info:
            TimeseriesQuery(
                point_names=["sensor_1"], start_time=sample_datetime, end_time=sample_datetime
            )

        errors = exc_info.value.errors()
        assert any("End time must be after start time" in error["msg"] for error in errors)


class TestWeatherModels:
    """Test the weather-related models."""

    def test_weather_point_sample_creation(self, sample_datetime):
        """Test creating a WeatherPointSample."""
        sample = WeatherPointSample(
            name="temperature",
            value=72.5,
            time=sample_datetime,
            units="fahrenheit",
            source="openweathermap",
        )

        assert sample.name == "temperature"
        assert sample.value == 72.5
        assert sample.units == "fahrenheit"
        assert sample.source == "openweathermap"

    def test_weather_point_sample_optional_fields(self, sample_datetime):
        """Test WeatherPointSample with optional fields."""
        sample = WeatherPointSample(name="temperature", value=72.5, time=sample_datetime)

        assert sample.units is None
        assert sample.source is None

    def test_weather_data_creation(self, sample_datetime):
        """Test creating WeatherData with all fields."""
        weather = WeatherData(
            temp=WeatherPointSample(name="temp", value=72.5, time=sample_datetime, units="F"),
            feels_like=WeatherPointSample(
                name="feels_like", value=75.0, time=sample_datetime, units="F"
            ),
            pressure=WeatherPointSample(
                name="pressure", value=1013.25, time=sample_datetime, units="hPa"
            ),
            humidity=WeatherPointSample(name="humidity", value=45, time=sample_datetime, units="%"),
            dew_point=WeatherPointSample(
                name="dew_point", value=52.0, time=sample_datetime, units="F"
            ),
            clouds=WeatherPointSample(name="clouds", value=25, time=sample_datetime, units="%"),
            wind_speed=WeatherPointSample(
                name="wind_speed", value=10.5, time=sample_datetime, units="mph"
            ),
            wind_deg=WeatherPointSample(
                name="wind_deg", value=180, time=sample_datetime, units="degrees"
            ),
            wet_bulb=WeatherPointSample(
                name="wet_bulb", value=60.0, time=sample_datetime, units="F"
            ),
        )

        assert weather.temp is not None and weather.temp.value == 72.5
        assert weather.humidity is not None and weather.humidity.value == 45
        assert weather.wind_speed is not None and weather.wind_speed.value == 10.5

    def test_weather_data_partial(self, sample_datetime):
        """Test WeatherData with only some fields."""
        weather = WeatherData(
            temp=WeatherPointSample(name="temp", value=72.5, time=sample_datetime),
            humidity=WeatherPointSample(name="humidity", value=45, time=sample_datetime),
        )

        assert weather.temp is not None and weather.temp.value == 72.5
        assert weather.humidity is not None and weather.humidity.value == 45
        assert weather.pressure is None
        assert weather.wind_speed is None


class TestAggregatedPointSample:
    """Test the AggregatedPointSample model."""

    def test_aggregated_point_sample_creation(self, sample_datetime):
        """Test creating a valid AggregatedPointSample."""
        agg_sample = AggregatedPointSample(
            name="temperature",
            timestamp=sample_datetime,
            count=10,
            min_value=68.0,
            max_value=75.0,
            avg_value=71.5,
            sum_value=715.0,
            std_dev=2.1,
        )

        assert agg_sample.name == "temperature"
        assert agg_sample.count == 10
        assert agg_sample.min_value == 68.0
        assert agg_sample.max_value == 75.0
        assert agg_sample.avg_value == 71.5
        assert agg_sample.sum_value == 715.0
        assert agg_sample.std_dev == 2.1

    def test_aggregated_point_sample_minimal(self, sample_datetime):
        """Test AggregatedPointSample with minimal fields."""
        agg_sample = AggregatedPointSample(name="temperature", timestamp=sample_datetime, count=0)

        assert agg_sample.count == 0
        assert agg_sample.min_value is None
        assert agg_sample.max_value is None
        assert agg_sample.avg_value is None
        assert agg_sample.sum_value is None
        assert agg_sample.std_dev is None

    def test_aggregated_point_sample_count_validation(self, sample_datetime):
        """Test count validation."""
        # Test negative count
        with pytest.raises(ValidationError) as exc_info:
            AggregatedPointSample(name="temperature", timestamp=sample_datetime, count=-1)

        errors = exc_info.value.errors()
        # The actual error message is from pydantic's ge constraint
        assert any(
            error["loc"] == ("count",) and "greater than or equal" in str(error["msg"])
            for error in errors
        )


class TestTimeseriesMetadata:
    """Test the TimeseriesMetadata model."""

    def test_timeseries_metadata_creation(self, sample_datetime):
        """Test creating TimeseriesMetadata."""
        metadata = TimeseriesMetadata(
            total_samples=100,
            start_time=sample_datetime,
            end_time=sample_datetime + timedelta(hours=1),
            sampling_interval=60.0,
            data_quality=0.95,
        )

        assert metadata.total_samples == 100
        assert metadata.sampling_interval == 60.0
        assert metadata.data_quality == 0.95

    def test_timeseries_metadata_minimal(self, sample_datetime):
        """Test TimeseriesMetadata with minimal fields."""
        metadata = TimeseriesMetadata(
            total_samples=0, start_time=sample_datetime, end_time=sample_datetime
        )

        assert metadata.total_samples == 0
        assert metadata.sampling_interval is None
        assert metadata.data_quality is None

    def test_timeseries_metadata_validation(self, sample_datetime):
        """Test metadata validation."""
        # Test negative total samples
        with pytest.raises(ValidationError) as exc_info:
            TimeseriesMetadata(
                total_samples=-1, start_time=sample_datetime, end_time=sample_datetime
            )

        errors = exc_info.value.errors()
        assert any("Total samples cannot be negative" in error["msg"] for error in errors)


class TestTimeseriesResponse:
    """Test the TimeseriesResponse model."""

    def test_timeseries_response_creation(self, sample_timeseries_data, sample_datetime):
        """Test creating TimeseriesResponse."""
        metadata = TimeseriesMetadata(
            total_samples=2,
            start_time=sample_datetime,
            end_time=sample_datetime + timedelta(hours=1),
        )

        response = TimeseriesResponse(
            point_samples=[PointSample(**s) for s in sample_timeseries_data["point_samples"]],
            metadata=metadata,
        )

        assert len(response.point_samples) == 2
        assert response.metadata is not None and response.metadata.total_samples == 2

    def test_timeseries_response_without_metadata(self, sample_point_sample_data):
        """Test TimeseriesResponse without metadata."""
        response = TimeseriesResponse(point_samples=[PointSample(**sample_point_sample_data)])

        assert len(response.point_samples) == 1
        assert response.metadata is None


class TestBulkTimeseriesData:
    """Test the BulkTimeseriesData model."""

    def test_bulk_timeseries_data_creation(self, sample_timeseries_data):
        """Test creating BulkTimeseriesData."""
        bulk_data = BulkTimeseriesData(
            data=[
                TimeseriesData(**sample_timeseries_data),
                TimeseriesData(**sample_timeseries_data),
            ]
        )

        assert len(bulk_data.data) == 2

    def test_bulk_timeseries_data_empty_validation(self):
        """Test validation for empty data list."""
        with pytest.raises(ValidationError) as exc_info:
            BulkTimeseriesData(data=[])

        errors = exc_info.value.errors()
        assert any("Bulk timeseries data cannot be empty" in error["msg"] for error in errors)


class TestUtilityFunctions:
    """Test the utility functions."""

    def test_create_point_sample(self):
        """Test create_point_sample function."""
        # Test with provided timestamp
        timestamp = datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)
        sample = create_point_sample("test_point", 42.5, timestamp)

        assert sample.name == "test_point"
        assert sample.value == 42.5
        assert sample.time == timestamp

        # Test without timestamp (should use current time)
        sample_no_time = create_point_sample("test_point", "string_value")
        assert sample_no_time.name == "test_point"
        assert sample_no_time.value == "string_value"
        assert isinstance(sample_no_time.time, datetime)
        assert sample_no_time.time.tzinfo is not None

    def test_filter_samples_by_time_range(self, sample_datetime):
        """Test filter_samples_by_time_range function."""
        base_time = sample_datetime
        samples = [
            PointSample(name="test", value=1, time=base_time - timedelta(hours=2)),
            PointSample(name="test", value=2, time=base_time - timedelta(hours=1)),
            PointSample(name="test", value=3, time=base_time),
            PointSample(name="test", value=4, time=base_time + timedelta(hours=1)),
            PointSample(name="test", value=5, time=base_time + timedelta(hours=2)),
        ]

        # Filter for middle 3 samples
        filtered = filter_samples_by_time_range(
            samples, base_time - timedelta(hours=1), base_time + timedelta(hours=1)
        )

        assert len(filtered) == 3
        assert filtered[0].value == 2
        assert filtered[1].value == 3
        assert filtered[2].value == 4

    def test_filter_samples_empty_list(self, sample_datetime):
        """Test filter_samples_by_time_range with empty list."""
        filtered = filter_samples_by_time_range(
            [], sample_datetime, sample_datetime + timedelta(hours=1)
        )
        assert filtered == []

    def test_group_samples_by_point(self, sample_datetime):
        """Test group_samples_by_point function."""
        samples = [
            PointSample(name="temp", value=72.5, time=sample_datetime),
            PointSample(name="humidity", value=45, time=sample_datetime),
            PointSample(name="temp", value=73.0, time=sample_datetime + timedelta(minutes=5)),
            PointSample(name="humidity", value=46, time=sample_datetime + timedelta(minutes=5)),
            PointSample(name="pressure", value=1013, time=sample_datetime),
        ]

        grouped = group_samples_by_point(samples)

        assert len(grouped) == 3
        assert len(grouped["temp"]) == 2
        assert len(grouped["humidity"]) == 2
        assert len(grouped["pressure"]) == 1
        assert grouped["temp"][0].value == 72.5
        assert grouped["temp"][1].value == 73.0

    def test_group_samples_empty_list(self):
        """Test group_samples_by_point with empty list."""
        grouped = group_samples_by_point([])
        assert grouped == {}

    def test_calculate_sampling_statistics(self, sample_datetime):
        """Test calculate_sampling_statistics function."""
        # Test with numeric values
        samples = [
            PointSample(name="test", value=10, time=sample_datetime),
            PointSample(name="test", value=20, time=sample_datetime),
            PointSample(name="test", value=30, time=sample_datetime),
            PointSample(name="test", value=40, time=sample_datetime),
            PointSample(name="test", value=50, time=sample_datetime),
        ]

        stats = calculate_sampling_statistics(samples)

        assert stats["count"] == 5
        assert stats["numeric_count"] == 5
        assert stats["min"] == 10
        assert stats["max"] == 50
        assert stats["avg"] == 30
        assert stats["sum"] == 150
        assert stats["std_dev"] == pytest.approx(14.142, rel=0.001)

    def test_calculate_sampling_statistics_mixed_types(self, sample_datetime):
        """Test statistics with mixed value types."""
        samples = [
            PointSample(name="test", value=10, time=sample_datetime),
            PointSample(name="test", value="not_a_number", time=sample_datetime),
            PointSample(name="test", value=20, time=sample_datetime),
            PointSample(name="test", value=None, time=sample_datetime),
            PointSample(name="test", value=30, time=sample_datetime),
        ]

        stats = calculate_sampling_statistics(samples)

        assert stats["count"] == 5
        assert stats["numeric_count"] == 3
        assert stats["min"] == 10
        assert stats["max"] == 30
        assert stats["avg"] == 20
        assert stats["sum"] == 60

    def test_calculate_sampling_statistics_no_numeric(self, sample_datetime):
        """Test statistics with no numeric values."""
        samples = [
            PointSample(name="test", value="string1", time=sample_datetime),
            PointSample(name="test", value="string2", time=sample_datetime),
            PointSample(name="test", value=None, time=sample_datetime),
        ]

        stats = calculate_sampling_statistics(samples)

        assert stats["count"] == 3
        assert stats["numeric_count"] == 0

    def test_calculate_sampling_statistics_empty(self):
        """Test statistics with empty list."""
        stats = calculate_sampling_statistics([])
        assert stats == {}

    def test_resample_timeseries(self, sample_datetime):
        """Test resample_timeseries function."""
        base_time = sample_datetime
        samples = []

        # Create samples every 30 seconds
        for i in range(10):
            samples.append(
                PointSample(
                    name="temperature", value=70 + i, time=base_time + timedelta(seconds=30 * i)
                )
            )

        # Resample to 60-second intervals
        resampled = resample_timeseries(samples, 60)

        assert len(resampled) > 0
        assert all(isinstance(s, AggregatedPointSample) for s in resampled)
        assert all(s.name == "temperature" for s in resampled)

        # Check that aggregation worked correctly
        first_bucket = resampled[0]
        assert first_bucket.count >= 1
        assert first_bucket.min_value is not None
        assert first_bucket.max_value is not None
        assert first_bucket.avg_value is not None

    def test_resample_timeseries_empty(self):
        """Test resample_timeseries with empty list."""
        resampled = resample_timeseries([], 60)
        assert resampled == []

    def test_resample_timeseries_single_sample(self, sample_datetime):
        """Test resample_timeseries with single sample."""
        sample = PointSample(name="test", value=42, time=sample_datetime)
        resampled = resample_timeseries([sample], 60)

        assert len(resampled) == 1
        assert resampled[0].count == 1
        assert resampled[0].min_value == 42
        assert resampled[0].max_value == 42
        assert resampled[0].avg_value == 42

    def test_validate_timeseries_data_quality(self, sample_datetime):
        """Test validate_timeseries_data_quality function."""
        base_time = sample_datetime

        # Test with regular interval samples
        regular_samples = []
        for i in range(10):
            regular_samples.append(
                PointSample(name="test", value=i * 10, time=base_time + timedelta(seconds=60 * i))
            )

        quality = validate_timeseries_data_quality(regular_samples, 60)
        assert quality > 0.9  # Should be high quality

        # Test with irregular intervals
        irregular_samples = [
            PointSample(name="test", value=1, time=base_time),
            PointSample(name="test", value=2, time=base_time + timedelta(seconds=60)),
            PointSample(name="test", value=3, time=base_time + timedelta(seconds=180)),  # Gap
            PointSample(name="test", value=4, time=base_time + timedelta(seconds=240)),
        ]

        quality_irregular = validate_timeseries_data_quality(irregular_samples, 60)
        assert quality_irregular < quality  # Should be lower quality

    def test_validate_timeseries_data_quality_with_nulls(self, sample_datetime):
        """Test quality validation with null values."""
        base_time = sample_datetime
        samples_with_nulls = [
            PointSample(name="test", value=1, time=base_time),
            PointSample(name="test", value=None, time=base_time + timedelta(seconds=60)),
            PointSample(name="test", value=3, time=base_time + timedelta(seconds=120)),
            PointSample(name="test", value=None, time=base_time + timedelta(seconds=180)),
            PointSample(name="test", value=5, time=base_time + timedelta(seconds=240)),
        ]

        quality = validate_timeseries_data_quality(samples_with_nulls, 60)
        assert 0.0 <= quality <= 1.0
        # With 2 nulls out of 5 samples, completeness is 0.6, and consistency is 1.0
        # Average quality should be (1.0 + 0.6) / 2 = 0.8
        assert quality == pytest.approx(0.8, rel=0.01)

    def test_validate_timeseries_data_quality_edge_cases(self, sample_datetime):
        """Test quality validation edge cases."""
        # Empty list
        assert validate_timeseries_data_quality([], 60) == 0.0

        # Single sample
        single_sample = [PointSample(name="test", value=42, time=sample_datetime)]
        assert validate_timeseries_data_quality(single_sample, 60) == 1.0

        # No expected interval
        samples = [
            PointSample(name="test", value=1, time=sample_datetime),
            PointSample(name="test", value=2, time=sample_datetime + timedelta(seconds=60)),
            PointSample(name="test", value=3, time=sample_datetime + timedelta(seconds=120)),
        ]
        quality = validate_timeseries_data_quality(samples)
        assert 0.0 <= quality <= 1.0


class TestModelIntegration:
    """Test model integration and complex scenarios."""

    def test_timeseries_workflow(self, sample_datetime):
        """Test a complete timeseries workflow."""
        # Create samples
        samples = []
        for i in range(20):
            samples.append(
                create_point_sample(
                    "temperature", 70 + (i % 5), sample_datetime + timedelta(minutes=i)
                )
            )

        # Filter by time range
        start = sample_datetime + timedelta(minutes=5)
        end = sample_datetime + timedelta(minutes=15)
        filtered = filter_samples_by_time_range(samples, start, end)

        assert len(filtered) == 11  # Minutes 5 through 15 inclusive

        # Calculate statistics
        stats = calculate_sampling_statistics(filtered)
        assert stats["count"] == 11
        assert stats["min"] == 70
        assert stats["max"] == 74

        # Resample to 5-minute intervals
        resampled = resample_timeseries(filtered, 300)  # 5 minutes = 300 seconds
        assert len(resampled) > 0

        # Validate quality
        quality = validate_timeseries_data_quality(filtered, 60)
        assert quality > 0.9  # Should be high quality for regular interval data

    def test_weather_data_workflow(self, sample_datetime):
        """Test weather data workflow."""
        # Create weather data
        weather = WeatherData(
            temp=WeatherPointSample(
                name="temperature",
                value=72.5,
                time=sample_datetime,
                units="F",
                source="openweathermap",
            ),
            humidity=WeatherPointSample(
                name="humidity", value=65, time=sample_datetime, units="%", source="openweathermap"
            ),
            pressure=WeatherPointSample(
                name="pressure",
                value=1013.25,
                time=sample_datetime,
                units="hPa",
                source="openweathermap",
            ),
        )

        # Convert to list of samples
        samples = []
        if weather.temp:
            samples.append(weather.temp)
        if weather.humidity:
            samples.append(weather.humidity)
        if weather.pressure:
            samples.append(weather.pressure)

        # Group by point
        grouped = group_samples_by_point(samples)
        assert len(grouped) == 3
        assert "temperature" in grouped
        assert "humidity" in grouped
        assert "pressure" in grouped

    def test_bulk_timeseries_processing(self, sample_datetime):
        """Test bulk timeseries processing."""
        # Create multiple timeseries datasets
        datasets = []

        for sensor in ["temp_sensor_1", "temp_sensor_2", "humidity_sensor_1"]:
            samples = []
            for i in range(5):
                samples.append(
                    PointSample(
                        name=sensor, value=20 + i, time=sample_datetime + timedelta(minutes=i * 10)
                    )
                )
            datasets.append(TimeseriesData(point_samples=samples))

        # Create bulk data
        bulk = BulkTimeseriesData(data=datasets)

        assert len(bulk.data) == 3

        # Process each dataset
        for ts_data in bulk.data:
            stats = calculate_sampling_statistics(ts_data.point_samples)
            assert stats["count"] == 5
            assert stats["min"] == 20
            assert stats["max"] == 24
