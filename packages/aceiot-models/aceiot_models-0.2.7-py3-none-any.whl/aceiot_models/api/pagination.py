"""Pagination utilities for ACE IoT API.

This module provides the PaginatedResults class for iterating over paginated API responses.
"""

from collections.abc import Callable, Iterator
from typing import Any


class PaginatedResults:
    """Iterator for paginated API results.

    This class provides a convenient way to iterate over all pages of a paginated API response,
    either page by page or by fetching all items at once.
    """

    def __init__(
        self,
        api_func: Callable[..., dict[str, Any]],
        per_page: int = 100,
        **kwargs: Any,
    ):
        """Initialize PaginatedResults.

        Args:
            api_func: API function to call for each page (must accept page and per_page params)
            per_page: Number of items per page
            **kwargs: Additional keyword arguments to pass to api_func
        """
        self.api_func = api_func
        self.per_page = per_page
        self.kwargs = kwargs
        self.current_page = 1
        self.total_pages = None
        self.total_items = None
        self._items_buffer: list[Any] = []

    def __iter__(self) -> Iterator[list[Any]]:
        """Iterate over pages of results.

        Yields:
            List of items for each page
        """
        self.current_page = 1
        self.total_pages = None
        self.total_items = None
        self._items_buffer = []

        while True:
            # Fetch current page
            response = self.api_func(page=self.current_page, per_page=self.per_page, **self.kwargs)

            # Extract pagination metadata
            if self.total_pages is None:
                self.total_pages = response.get("total_pages", 1)
                self.total_items = response.get("total_items", 0)

            # Extract items
            items = response.get("items", [])
            if not items:
                break

            yield items

            # Check if we've reached the last page
            if self.current_page >= self.total_pages:
                break

            self.current_page += 1

    def all_items(self) -> list[Any]:
        """Fetch all items from all pages at once.

        Returns:
            List of all items across all pages
        """
        all_items = []
        for page_items in self:
            all_items.extend(page_items)
        return all_items

    def pages(self) -> Iterator[dict[str, Any]]:
        """Iterate over full page responses including metadata.

        Yields:
            Full response dict for each page
        """
        self.current_page = 1
        self.total_pages = None
        self.total_items = None

        while True:
            # Fetch current page
            response = self.api_func(page=self.current_page, per_page=self.per_page, **self.kwargs)

            # Extract pagination metadata
            if self.total_pages is None:
                self.total_pages = response.get("total_pages", 1)
                self.total_items = response.get("total_items", 0)

            yield response

            # Check if we've reached the last page or no items
            items = response.get("items", [])
            if not items or self.current_page >= self.total_pages:
                break

            self.current_page += 1

    def first_page(self) -> list[Any]:
        """Get only the first page of results.

        Returns:
            List of items from the first page
        """
        response = self.api_func(page=1, per_page=self.per_page, **self.kwargs)
        return response.get("items", [])
