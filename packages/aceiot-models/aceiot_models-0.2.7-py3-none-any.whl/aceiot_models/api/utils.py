"""Utility functions for ACE IoT API operations.

This module provides helper functions for pagination, batch processing,
and data transformation when working with the ACE IoT API.
"""

from collections.abc import Callable
from datetime import datetime
from typing import Any, TypeVar

from ..points import Point, PointCreate
from ..sample import Sample
from .pagination import PaginatedResults


T = TypeVar("T")


def get_api_results_paginated(
    api_func: Callable[..., dict[str, Any]],
    per_page: int = 500,
    max_items: int | None = None,
    **kwargs: Any,
) -> list[Any]:
    """Get all results from a paginated API endpoint.

    Args:
        api_func: API function to call
        per_page: Number of items per page
        max_items: Maximum number of items to fetch (None for all)
        **kwargs: Additional arguments to pass to api_func

    Returns:
        List of all items
    """
    paginator = PaginatedResults(api_func, per_page=per_page, **kwargs)
    all_items = []

    for page_items in paginator:
        all_items.extend(page_items)
        if max_items and len(all_items) >= max_items:
            return all_items[:max_items]

    return all_items


def batch_process(
    items: list[T],
    process_func: Callable[[list[T]], Any],
    batch_size: int = 100,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[Any]:
    """Process items in batches.

    Args:
        items: Items to process
        process_func: Function to process each batch
        batch_size: Size of each batch
        progress_callback: Optional callback for progress updates (current, total)

    Returns:
        List of results from each batch
    """
    results = []
    total_items = len(items)

    for i in range(0, total_items, batch_size):
        batch = items[i : i + batch_size]
        result = process_func(batch)
        results.append(result)

        if progress_callback:
            progress_callback(min(i + batch_size, total_items), total_items)

    return results


def process_points_from_api(api_points: list[dict[str, Any]]) -> list[Point]:
    """Process points from API response into Point models.

    Args:
        api_points: List of point data from API

    Returns:
        List of Point model instances
    """
    points = []
    for point_data in api_points:
        # Convert API response to Point model
        # Extract tags into marker_tags and kv_tags format
        tags = point_data.get("tags", {})
        marker_tags = tags.get("markers", []) if isinstance(tags, dict) else []
        kv_tags = (
            {k: v for k, v in tags.items() if k != "markers"} if isinstance(tags, dict) else {}
        )

        # Build point data dict with only provided fields
        point_dict: dict[str, Any] = {
            "name": point_data.get("name", ""),  # Required field
            "client_id": point_data.get("client_id", 0),  # Required field
            "site_id": point_data.get("site_id", 0),  # Required field
            "marker_tags": marker_tags,
            "kv_tags": kv_tags,
        }

        # Add optional fields only if present
        if "id" in point_data:
            point_dict["id"] = point_data["id"]
        if "client" in point_data:
            point_dict["client"] = point_data["client"]
        if "site" in point_data:
            point_dict["site"] = point_data["site"]
        if "point_type" in point_data:
            point_dict["point_type"] = point_data["point_type"]
        if "bacnet_data" in point_data:
            point_dict["bacnet_data"] = point_data["bacnet_data"]
        if "collect_config" in point_data:
            point_dict["collect_config"] = point_data["collect_config"]
        if "collect_enabled" in point_data:
            point_dict["collect_enabled"] = point_data["collect_enabled"]
        if "collect_interval" in point_data:
            point_dict["collect_interval"] = point_data["collect_interval"]
        if "topic_id" in point_data:
            point_dict["topic_id"] = point_data["topic_id"]
        if "device_id" in point_data:
            point_dict["device_id"] = point_data["device_id"]
        if "created" in point_data or "created_at" in point_data:
            point_dict["created"] = point_data.get("created") or point_data.get("created_at")
        if "updated" in point_data or "updated_at" in point_data:
            point_dict["updated"] = point_data.get("updated") or point_data.get("updated_at")

        point = Point(**point_dict)
        points.append(point)
    return points


def convert_api_response_to_points(response: dict[str, Any]) -> list[Point]:
    """Convert API paginated response to Point models.

    Args:
        response: API response with 'items' key

    Returns:
        List of Point model instances
    """
    items = response.get("items", [])
    return process_points_from_api(items)


def convert_samples_to_models(samples_data: list[dict[str, Any]]) -> list[Sample]:
    """Convert sample data from API to Sample models.

    Args:
        samples_data: List of sample data from API

    Returns:
        List of Sample model instances
    """
    samples = []
    for sample_data in samples_data:
        try:
            # Use the from_api_model classmethod
            sample = Sample.from_api_model(sample_data)
            samples.append(sample)
        except (KeyError, ValueError, TypeError):
            # Fallback for malformed data - try to extract what we can
            time_str = sample_data.get("time") or sample_data.get("timestamp")
            if time_str and sample_data.get("name") and "value" in sample_data:
                try:
                    sample = Sample(
                        name=sample_data["name"],
                        time=datetime.fromisoformat(time_str),
                        value=float(sample_data["value"]),
                    )
                    samples.append(sample)
                except (ValueError, TypeError):
                    # Skip this sample if we can't parse it
                    continue
    return samples


def prepare_point_for_creation(point_data: dict[str, Any] | PointCreate) -> dict[str, Any]:
    """Prepare point data for API creation.

    Args:
        point_data: Point data as dict or PointCreate model

    Returns:
        Dict ready for API
    """
    if isinstance(point_data, PointCreate):
        # Convert model to dict, excluding None values
        return {k: v for k, v in point_data.model_dump().items() if v is not None}
    return point_data


def group_points_by_site(points: list[Point]) -> dict[int, list[Point]]:
    """Group points by site ID.

    Args:
        points: List of points

    Returns:
        Dict mapping site_id to list of points
    """
    grouped = {}
    for point in points:
        if point.site_id:
            if point.site_id not in grouped:
                grouped[point.site_id] = []
            grouped[point.site_id].append(point)
    return grouped


def filter_points_by_type(points: list[Point], point_type: str) -> list[Point]:
    """Filter points by type.

    Args:
        points: List of points
        point_type: Type to filter by

    Returns:
        Filtered list of points
    """
    return [p for p in points if p.point_type == point_type]


def extract_point_paths(points: list[Point]) -> list[str]:
    """Extract hierarchical paths from point names.

    Args:
        points: List of points

    Returns:
        List of unique paths
    """
    paths = set()
    for point in points:
        if point.name:
            # Extract path components (e.g., "building/floor/room/device" -> ["building", "floor", "room"])
            parts = point.name.split("/")
            for i in range(1, len(parts)):
                path = "/".join(parts[:i])
                paths.add(path)
    return sorted(paths)
