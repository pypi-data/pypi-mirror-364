"""Tests for pagination utilities."""

import pytest

from aceiot_models.api.pagination import PaginatedResults


class TestPaginatedResults:
    """Test cases for PaginatedResults."""

    @pytest.fixture
    def mock_api_func(self):
        """Create mock API function that returns paginated results."""

        # Create a function that returns different pages
        def api_func(page=1, per_page=10, **kwargs):
            if page == 1:
                return {
                    "items": [{"id": i, "name": f"Item {i}"} for i in range(1, 11)],
                    "page": 1,
                    "per_page": 10,
                    "total_pages": 3,
                    "total_items": 25,
                }
            elif page == 2:
                return {
                    "items": [{"id": i, "name": f"Item {i}"} for i in range(11, 21)],
                    "page": 2,
                    "per_page": 10,
                    "total_pages": 3,
                    "total_items": 25,
                }
            elif page == 3:
                return {
                    "items": [{"id": i, "name": f"Item {i}"} for i in range(21, 26)],
                    "page": 3,
                    "per_page": 10,
                    "total_pages": 3,
                    "total_items": 25,
                }
            else:
                return {
                    "items": [],
                    "page": page,
                    "per_page": 10,
                    "total_pages": 3,
                    "total_items": 25,
                }

        return api_func

    @pytest.fixture
    def empty_api_func(self):
        """Create mock API function that returns no results."""

        def api_func(page=1, per_page=10, **kwargs):
            return {
                "items": [],
                "page": 1,
                "per_page": 10,
                "total_pages": 0,
                "total_items": 0,
            }

        return api_func

    def test_init(self, mock_api_func):
        """Test PaginatedResults initialization."""
        paginator = PaginatedResults(mock_api_func, per_page=20, client_id=1)
        assert paginator.api_func == mock_api_func
        assert paginator.per_page == 20
        assert paginator.kwargs == {"client_id": 1}
        assert paginator.current_page == 1
        assert paginator.total_pages is None
        assert paginator.total_items is None

    def test_iterate_pages(self, mock_api_func):
        """Test iterating over pages."""
        paginator = PaginatedResults(mock_api_func, per_page=10)
        pages = list(paginator)

        assert len(pages) == 3
        assert len(pages[0]) == 10  # First page
        assert len(pages[1]) == 10  # Second page
        assert len(pages[2]) == 5  # Third page (partial)
        assert pages[0][0]["name"] == "Item 1"
        assert pages[1][0]["name"] == "Item 11"
        assert pages[2][0]["name"] == "Item 21"

    def test_all_items(self, mock_api_func):
        """Test fetching all items at once."""
        paginator = PaginatedResults(mock_api_func, per_page=10)
        all_items = paginator.all_items()

        assert len(all_items) == 25
        assert all_items[0]["name"] == "Item 1"
        assert all_items[24]["name"] == "Item 25"

    def test_pages_iterator(self, mock_api_func):
        """Test iterating over full page responses."""
        paginator = PaginatedResults(mock_api_func, per_page=10)
        pages = list(paginator.pages())

        assert len(pages) == 3
        assert pages[0]["page"] == 1
        assert pages[0]["total_pages"] == 3
        assert pages[0]["total_items"] == 25
        assert len(pages[0]["items"]) == 10

    def test_first_page(self, mock_api_func):
        """Test getting only the first page."""
        paginator = PaginatedResults(mock_api_func, per_page=10)
        first_page = paginator.first_page()

        assert len(first_page) == 10
        assert first_page[0]["name"] == "Item 1"
        assert first_page[9]["name"] == "Item 10"

    def test_empty_results(self, empty_api_func):
        """Test handling empty results."""
        paginator = PaginatedResults(empty_api_func, per_page=10)

        # Test iteration
        pages = list(paginator)
        assert len(pages) == 0

        # Test all_items
        all_items = paginator.all_items()
        assert len(all_items) == 0

        # Test first_page
        first_page = paginator.first_page()
        assert len(first_page) == 0

    def test_single_page_results(self):
        """Test handling single page of results."""

        def single_page_api(page=1, per_page=10, **kwargs):
            if page == 1:
                return {
                    "items": [{"id": i} for i in range(1, 6)],
                    "page": 1,
                    "per_page": 10,
                    "total_pages": 1,
                    "total_items": 5,
                }
            else:
                return {
                    "items": [],
                    "page": page,
                    "per_page": 10,
                    "total_pages": 1,
                    "total_items": 5,
                }

        paginator = PaginatedResults(single_page_api, per_page=10)
        pages = list(paginator)

        assert len(pages) == 1
        assert len(pages[0]) == 5

    def test_reset_on_iteration(self, mock_api_func):
        """Test that iteration resets state."""
        paginator = PaginatedResults(mock_api_func, per_page=10)

        # First iteration
        first_run = list(paginator)
        assert len(first_run) == 3

        # Second iteration should reset and work correctly
        second_run = list(paginator)
        assert len(second_run) == 3
        assert first_run[0][0]["id"] == second_run[0][0]["id"]

    def test_kwargs_passed_to_api_func(self):
        """Test that kwargs are properly passed to API function."""
        called_with = []

        def tracking_api_func(page=1, per_page=10, **kwargs):
            called_with.append(kwargs)
            return {"items": [{"id": 1}], "total_pages": 1}

        paginator = PaginatedResults(tracking_api_func, per_page=5, site_id=123, active=True)
        list(paginator)

        assert called_with[0] == {"site_id": 123, "active": True}

    def test_missing_pagination_metadata(self):
        """Test handling of missing pagination metadata."""

        def no_metadata_api(page=1, per_page=10, **kwargs):
            if page == 1:
                return {"items": [{"id": 1}, {"id": 2}]}
            else:
                return {"items": []}

        paginator = PaginatedResults(no_metadata_api, per_page=10)
        pages = list(paginator)

        # Should handle missing metadata gracefully
        assert len(pages) == 1
        assert len(pages[0]) == 2
