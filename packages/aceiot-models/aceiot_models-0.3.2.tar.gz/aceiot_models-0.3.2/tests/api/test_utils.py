"""Tests for API utility functions."""

from aceiot_models.api.utils import (
    batch_process,
    convert_api_response_to_points,
    convert_samples_to_models,
    extract_point_paths,
    filter_points_by_type,
    get_api_results_paginated,
    group_points_by_site,
    prepare_point_for_creation,
    process_points_from_api,
)
from aceiot_models.points import Point, PointCreate
from aceiot_models.sample import Sample


class TestAPIUtils:
    """Test cases for API utility functions."""

    def test_get_api_results_paginated(self):
        """Test get_api_results_paginated function."""

        # Mock API function that returns paginated results
        def mock_api_func(page=1, per_page=10, **kwargs):
            if page == 1:
                return {
                    "items": [{"id": i} for i in range(1, 11)],
                    "total_pages": 2,
                    "total_items": 15,
                }
            elif page == 2:
                return {
                    "items": [{"id": i} for i in range(11, 16)],
                    "total_pages": 2,
                    "total_items": 15,
                }
            else:
                return {"items": []}

        # Test getting all results
        results = get_api_results_paginated(mock_api_func, per_page=10)
        assert len(results) == 15
        assert results[0]["id"] == 1
        assert results[14]["id"] == 15

        # Test with max_items
        results = get_api_results_paginated(mock_api_func, per_page=10, max_items=7)
        assert len(results) == 7

    def test_batch_process(self):
        """Test batch_process function."""
        items = list(range(1, 26))  # 25 items
        processed_batches = []

        def process_func(batch):
            processed_batches.append(len(batch))
            return sum(batch)

        # Test without progress callback
        results = batch_process(items, process_func, batch_size=10)
        assert len(results) == 3  # 3 batches
        assert processed_batches == [10, 10, 5]
        assert results[0] == sum(range(1, 11))  # Sum of first batch

        # Test with progress callback
        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        processed_batches = []
        results = batch_process(
            items, process_func, batch_size=10, progress_callback=progress_callback
        )
        assert progress_calls == [(10, 25), (20, 25), (25, 25)]

    def test_process_points_from_api(self):
        """Test process_points_from_api function."""
        api_points = [
            {
                "id": 1,
                "name": "sensor/temp",
                "client_id": 1,
                "site_id": 1,
                "point_type": "analog",
                "tags": {"markers": ["temp", "room1"], "location": "room1"},
                "bacnet_data": {"device_id": 123},
                "collect_enabled": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": 2,
                "name": "sensor/humidity",
                "client_id": 1,
                "site_id": 1,
            },
        ]

        points = process_points_from_api(api_points)
        assert len(points) == 2
        assert isinstance(points[0], Point)
        assert points[0].id == 1
        assert points[0].name == "sensor/temp"
        assert points[0].marker_tags == ["temp", "room1"]
        assert points[0].kv_tags == {"location": "room1"}
        assert points[1].id == 2
        assert points[1].name == "sensor/humidity"

    def test_convert_api_response_to_points(self):
        """Test convert_api_response_to_points function."""
        response = {
            "items": [
                {"id": 1, "name": "point1", "site_id": 1, "client_id": 1},
                {"id": 2, "name": "point2", "site_id": 1, "client_id": 1},
            ],
            "total_pages": 1,
        }

        points = convert_api_response_to_points(response)
        assert len(points) == 2
        assert all(isinstance(p, Point) for p in points)
        assert points[0].name == "point1"

    def test_convert_samples_to_models(self):
        """Test convert_samples_to_models function."""
        samples_data = [
            {
                "name": "sensor/temp",
                "time": "2024-01-01T00:00:00",
                "value": "23.5",
            },
            {
                "name": "sensor/humidity",
                "time": "2024-01-01T00:00:00",
                "value": "65.0",
            },
        ]

        samples = convert_samples_to_models(samples_data)
        assert len(samples) == 2
        assert isinstance(samples[0], Sample)
        assert samples[0].name == "sensor/temp"
        assert samples[0].value == 23.5
        assert samples[1].name == "sensor/humidity"

    def test_prepare_point_for_creation_with_dict(self):
        """Test prepare_point_for_creation with dict input."""
        point_data = {
            "name": "new/point",
            "site_id": 1,
            "description": "Test point",
        }

        result = prepare_point_for_creation(point_data)
        assert result == point_data

    def test_prepare_point_for_creation_with_model(self):
        """Test prepare_point_for_creation with PointCreate model."""
        point_model = PointCreate(
            name="new/point",
            site_id=1,
            client_id=1,
            point_type="analog",
            collect_enabled=True,
        )

        result = prepare_point_for_creation(point_model)
        assert "name" in result
        assert result["name"] == "new/point"
        assert result["site_id"] == 1
        assert result["client_id"] == 1

    def test_group_points_by_site(self):
        """Test group_points_by_site function."""
        points = [
            Point(id=1, name="p1", site_id=1, client_id=1),
            Point(id=2, name="p2", site_id=1, client_id=1),
            Point(id=3, name="p3", site_id=2, client_id=1),
        ]

        grouped = group_points_by_site(points)
        assert len(grouped) == 2
        assert len(grouped[1]) == 2
        assert len(grouped[2]) == 1
        assert grouped[1][0].name == "p1"
        assert grouped[2][0].name == "p3"

    def test_filter_points_by_type(self):
        """Test filter_points_by_type function."""
        points = [
            Point(id=1, name="p1", point_type="analog", site_id=1, client_id=1),
            Point(id=2, name="p2", point_type="digital", site_id=1, client_id=1),
            Point(id=3, name="p3", point_type="analog", site_id=1, client_id=1),
            Point(id=4, name="p4", point_type="multistate", site_id=1, client_id=1),
        ]

        analog_points = filter_points_by_type(points, "analog")
        assert len(analog_points) == 2
        assert all(p.point_type == "analog" for p in analog_points)

        digital_points = filter_points_by_type(points, "digital")
        assert len(digital_points) == 1
        assert digital_points[0].name == "p2"

    def test_extract_point_paths(self):
        """Test extract_point_paths function."""
        points = [
            Point(id=1, name="building/floor1/room1/temp", site_id=1, client_id=1),
            Point(id=2, name="building/floor1/room2/temp", site_id=1, client_id=1),
            Point(id=3, name="building/floor2/room1/temp", site_id=1, client_id=1),
            Point(id=4, name="outdoor/weather/temp", site_id=1, client_id=1),
            Point(id=5, name="single", site_id=1, client_id=1),  # No path
        ]

        paths = extract_point_paths(points)
        expected_paths = [
            "building",
            "building/floor1",
            "building/floor1/room1",
            "building/floor1/room2",
            "building/floor2",
            "building/floor2/room1",
            "outdoor",
            "outdoor/weather",
        ]
        assert paths == sorted(expected_paths)

    def test_extract_point_paths_no_duplicates(self):
        """Test extract_point_paths removes duplicates."""
        points = [
            Point(id=1, name="a/b/c", site_id=1, client_id=1),
            Point(id=2, name="a/b/d", site_id=1, client_id=1),
            Point(id=3, name="a/b/e", site_id=1, client_id=1),
        ]

        paths = extract_point_paths(points)
        assert paths == ["a", "a/b"]
        assert len(paths) == 2  # No duplicates
