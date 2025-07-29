"""Timeseries data models for ACE IoT API."""

from datetime import UTC, datetime
from typing import Any

from pydantic import Field, field_validator

from .common import BaseModel


class PointSample(BaseModel):
    """Point sample model for timeseries data."""

    name: str = Field(..., description="Point Name")
    value: str | int | float | bool | None = Field(..., description="Point Sample Value")
    time: datetime = Field(..., description="Sample timestamp")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate point name is not empty."""
        if not v or not v.strip():
            raise ValueError("Point name cannot be empty")
        return v.strip()

    @field_validator("time")
    @classmethod
    def validate_time_not_none(cls, v: datetime) -> datetime:
        """Validate timestamp is provided."""
        if v is None:
            raise ValueError("Sample timestamp is required")
        return v


class TimeseriesData(BaseModel):
    """Container for multiple point samples."""

    point_samples: list[PointSample] = Field(..., description="List of point samples")

    @field_validator("point_samples")
    @classmethod
    def validate_point_samples_not_empty(cls, v: list[PointSample]) -> list[PointSample]:
        """Validate that point samples list is not empty."""
        if not v:
            raise ValueError("Point samples list cannot be empty")
        return v


class TimeseriesQuery(BaseModel):
    """Query parameters for timeseries data requests."""

    point_names: list[str] = Field(..., description="List of point names to query")
    start_time: datetime = Field(..., description="Start time for query")
    end_time: datetime = Field(..., description="End time for query")

    @field_validator("point_names")
    @classmethod
    def validate_point_names(cls, v: list[str]) -> list[str]:
        """Validate point names list."""
        if not v:
            raise ValueError("At least one point name must be provided")

        validated_names = []
        for name in v:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("All point names must be non-empty strings")
            validated_names.append(name.strip())

        return validated_names

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v: datetime, values) -> datetime:
        """Validate that end time is after start time."""
        if hasattr(values, "data") and "start_time" in values.data:
            start_time = values.data["start_time"]
            if start_time and v <= start_time:
                raise ValueError("End time must be after start time")
        return v


class WeatherPointSample(PointSample):
    """Specialized point sample for weather data."""

    units: str | None = Field(None, description="Units of measurement")
    source: str | None = Field(None, description="Data source")


class WeatherData(BaseModel):
    """Weather data model with common weather parameters."""

    temp: WeatherPointSample | None = Field(None, description="Temperature")
    feels_like: WeatherPointSample | None = Field(None, description="Feels like temperature")
    pressure: WeatherPointSample | None = Field(None, description="Atmospheric pressure")
    humidity: WeatherPointSample | None = Field(None, description="Humidity percentage")
    dew_point: WeatherPointSample | None = Field(None, description="Dew point temperature")
    clouds: WeatherPointSample | None = Field(None, description="Cloud cover percentage")
    wind_speed: WeatherPointSample | None = Field(None, description="Wind speed")
    wind_deg: WeatherPointSample | None = Field(None, description="Wind direction in degrees")
    wet_bulb: WeatherPointSample | None = Field(None, description="Wet bulb temperature")


class AggregatedPointSample(BaseModel):
    """Aggregated point sample with statistical information."""

    name: str = Field(..., description="Point name")
    timestamp: datetime = Field(..., description="Aggregation timestamp")
    count: int = Field(
        0, ge=0, description="Number of samples in aggregation"
    )  # pyrefly: ignore[no-matching-overload]
    min_value: float | None = Field(None, description="Minimum value")
    max_value: float | None = Field(None, description="Maximum value")
    avg_value: float | None = Field(None, description="Average value")
    sum_value: float | None = Field(None, description="Sum of values")
    std_dev: float | None = Field(None, description="Standard deviation")

    @field_validator("count")
    @classmethod
    def validate_count_positive(cls, v: int) -> int:
        """Validate count is non-negative."""
        if v < 0:
            raise ValueError("Count cannot be negative")
        return v


class TimeseriesMetadata(BaseModel):
    """Metadata for timeseries queries."""

    total_samples: int = Field(..., description="Total number of samples")
    start_time: datetime = Field(..., description="Actual start time of data")
    end_time: datetime = Field(..., description="Actual end time of data")
    sampling_interval: float | None = Field(
        None, description="Average sampling interval in seconds"
    )
    data_quality: float | None = Field(None, description="Data quality score (0-1)")

    @field_validator("total_samples")
    @classmethod
    def validate_total_samples(cls, v: int) -> int:
        """Validate total samples is non-negative."""
        if v < 0:
            raise ValueError("Total samples cannot be negative")
        return v


class TimeseriesResponse(BaseModel):
    """Complete timeseries response with data and metadata."""

    point_samples: list[PointSample] = Field(..., description="Point sample data")
    metadata: TimeseriesMetadata | None = Field(None, description="Query metadata")


class BulkTimeseriesData(BaseModel):
    """Bulk timeseries data for multiple points."""

    data: list[TimeseriesData] = Field(..., description="List of timeseries data sets")

    @field_validator("data")
    @classmethod
    def validate_data_not_empty(cls, v: list[TimeseriesData]) -> list[TimeseriesData]:
        """Validate data list is not empty."""
        if not v:
            raise ValueError("Bulk timeseries data cannot be empty")
        return v


# Utility functions
def create_point_sample(name: str, value: Any, timestamp: datetime | None = None) -> PointSample:
    """Create a point sample with current timestamp if not provided."""
    if timestamp is None:
        timestamp = datetime.now(UTC)

    return PointSample(name=name, value=value, time=timestamp)


def filter_samples_by_time_range(
    samples: list[PointSample], start_time: datetime, end_time: datetime
) -> list[PointSample]:
    """Filter point samples by time range."""
    return [sample for sample in samples if start_time <= sample.time <= end_time]


def group_samples_by_point(samples: list[PointSample]) -> dict[str, list[PointSample]]:
    """Group point samples by point name."""
    grouped = {}
    for sample in samples:
        if sample.name not in grouped:
            grouped[sample.name] = []
        grouped[sample.name].append(sample)

    return grouped


def calculate_sampling_statistics(samples: list[PointSample]) -> dict:
    """Calculate basic statistics for a list of samples."""
    if not samples:
        return {}

    # Extract numeric values only
    numeric_values = []
    for sample in samples:
        try:
            if sample.value is not None:
                numeric_values.append(float(sample.value))
        except (ValueError, TypeError):
            continue

    if not numeric_values:
        return {"count": len(samples), "numeric_count": 0}

    # Calculate basic statistics
    count = len(numeric_values)
    sum_values = sum(numeric_values)
    avg = sum_values / count

    # Calculate standard deviation
    squared_diffs = [(x - avg) ** 2 for x in numeric_values]
    variance = sum(squared_diffs) / count
    std_dev = variance**0.5

    return {
        "count": len(samples),
        "numeric_count": count,
        "min": min(numeric_values),
        "max": max(numeric_values),
        "avg": avg,
        "sum": sum_values,
        "std_dev": std_dev,
    }


def resample_timeseries(
    samples: list[PointSample], interval_seconds: int
) -> list[AggregatedPointSample]:
    """Resample timeseries data to specified interval with aggregation."""
    if not samples:
        return []

    # Group samples by time buckets
    from collections import defaultdict

    buckets: dict[datetime, list[PointSample]] = defaultdict(list)

    # Use the first sample's timestamp as reference
    reference_time = samples[0].time
    reference_timestamp = reference_time.timestamp()

    for sample in samples:
        # Calculate which bucket this sample belongs to
        sample_timestamp = sample.time.timestamp()
        bucket_index = int((sample_timestamp - reference_timestamp) // interval_seconds)
        bucket_time = datetime.fromtimestamp(
            reference_timestamp + (bucket_index * interval_seconds)
        )
        buckets[bucket_time].append(sample)

    # Create aggregated samples
    aggregated_samples = []

    for timestamp, bucket_samples in sorted(buckets.items()):
        if not bucket_samples:
            continue

        # Calculate statistics for this bucket
        stats = calculate_sampling_statistics(bucket_samples)
        point_name = bucket_samples[0].name

        aggregated_sample = AggregatedPointSample(
            name=point_name,
            timestamp=timestamp,
            count=stats.get("count", 0),
            min_value=stats.get("min"),
            max_value=stats.get("max"),
            avg_value=stats.get("avg"),
            sum_value=stats.get("sum"),
            std_dev=stats.get("std_dev"),
        )

        aggregated_samples.append(aggregated_sample)

    return aggregated_samples


def validate_timeseries_data_quality(
    samples: list[PointSample], expected_interval_seconds: int | None = None
) -> float:
    """Validate timeseries data quality and return quality score (0-1)."""
    if not samples:
        return 0.0

    if len(samples) == 1:
        return 1.0

    # Sort samples by time
    sorted_samples = sorted(samples, key=lambda x: x.time)

    # Calculate intervals between samples
    intervals = []
    for i in range(1, len(sorted_samples)):
        interval = (sorted_samples[i].time - sorted_samples[i - 1].time).total_seconds()
        intervals.append(interval)

    if not intervals:
        return 1.0

    # If expected interval is provided, check consistency
    if expected_interval_seconds:
        # Calculate how many samples have intervals close to expected
        tolerance = expected_interval_seconds * 0.1  # 10% tolerance
        consistent_intervals = sum(
            1 for interval in intervals if abs(interval - expected_interval_seconds) <= tolerance
        )
        consistency_score = consistent_intervals / len(intervals)
    else:
        # If no expected interval, just check for reasonable consistency
        avg_interval = sum(intervals) / len(intervals)
        tolerance = avg_interval * 0.2  # 20% tolerance
        consistent_intervals = sum(
            1 for interval in intervals if abs(interval - avg_interval) <= tolerance
        )
        consistency_score = consistent_intervals / len(intervals)

    # Check for missing values
    null_values = sum(1 for sample in samples if sample.value is None)
    completeness_score = 1.0 - (null_values / len(samples))

    # Overall quality is average of consistency and completeness
    quality_score = (consistency_score + completeness_score) / 2

    return min(max(quality_score, 0.0), 1.0)


# Export all models
__all__ = [
    "AggregatedPointSample",
    "BulkTimeseriesData",
    "PointSample",
    "TimeseriesData",
    "TimeseriesMetadata",
    "TimeseriesQuery",
    "TimeseriesResponse",
    "WeatherData",
    "WeatherPointSample",
    "calculate_sampling_statistics",
    "create_point_sample",
    "filter_samples_by_time_range",
    "group_samples_by_point",
    "resample_timeseries",
    "validate_timeseries_data_quality",
]
