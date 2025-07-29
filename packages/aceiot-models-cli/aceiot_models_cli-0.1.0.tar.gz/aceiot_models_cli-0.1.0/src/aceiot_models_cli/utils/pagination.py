"""Pagination utilities for API responses."""

from collections.abc import Iterator
from typing import Any


class PaginatedResults:
    """Iterator for paginated API results."""

    def __init__(
        self, api_func, per_page: int = 500, initial_params: dict[str, Any] | None = None, **kwargs
    ):
        """Initialize paginated results iterator.

        Args:
            api_func: Function to call for each page
            per_page: Number of items per page
            initial_params: Initial parameters for API call
            **kwargs: Additional keyword arguments for api_func
        """
        self.api_func = api_func
        self.per_page = per_page
        self.params = initial_params or {}
        self.kwargs = kwargs
        self.current_page = 1
        self.total_pages = None
        self.exhausted = False

    def __iter__(self) -> Iterator[list[Any]]:
        """Return iterator."""
        return self

    def __next__(self) -> list[Any]:
        """Get next page of results."""
        if self.exhausted:
            raise StopIteration

        # Update params with current page
        self.params.update({"per_page": self.per_page, "page": self.current_page})

        # Call API function
        response = self.api_func(params=self.params, **self.kwargs)

        # Extract items and pagination info
        items = response.get("items", [])
        self.total_pages = response.get("pages", 1)

        # Check if we've reached the last page
        if self.current_page >= self.total_pages:
            self.exhausted = True
        else:
            self.current_page += 1

        return items

    def all_items(self) -> list[Any]:
        """Get all items from all pages.

        Returns:
            List of all items across all pages
        """
        all_items = []
        for page_items in self:
            all_items.extend(page_items)
        return all_items
