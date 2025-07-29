"""API helper utilities for common operations."""

import logging
from collections.abc import Callable, Iterator
from typing import Any, TypeVar

from ..api_client import APIClient

logger = logging.getLogger(__name__)

T = TypeVar("T")


def get_api_results_paginated(
    client: APIClient,
    endpoint: str,
    per_page: int = 500,
    params: dict[str, Any] | None = None,
) -> Iterator[dict[str, Any]]:
    """Get paginated results from API endpoint.

    Automatically handles pagination by yielding each page of results.

    Args:
        client: APIClient instance
        endpoint: API endpoint to call
        per_page: Number of items per page
        params: Additional parameters for API call

    Yields:
        Dictionary containing page data with 'items' key
    """
    if params is None:
        params = {}

    page = 1
    while True:
        # Create a copy of params and update with pagination
        request_params = params.copy()
        request_params.update({"per_page": per_page, "page": page})

        # Make API request
        response = client._make_request("GET", endpoint, params=request_params)

        # Yield the response
        yield response

        # Check if we've reached the last page
        if response.get("page", 1) >= response.get("pages", 1):
            break

        page += 1


def post_to_api(
    client: APIClient,
    endpoint: str,
    data: dict[str, Any],
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generic POST helper for API operations.

    Args:
        client: APIClient instance
        endpoint: API endpoint to call
        data: Data to POST
        params: Query parameters

    Returns:
        API response dictionary
    """
    return client._make_request("POST", endpoint, json_data=data, params=params)


def batch_process(
    items: list[T],
    process_func: Callable[[list[T]], Any],
    batch_size: int = 100,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[Any]:
    """Process items in batches.

    Useful for APIs with limits on bulk operations.

    Args:
        items: List of items to process
        process_func: Function to process each batch
        batch_size: Maximum items per batch
        progress_callback: Optional callback for progress updates (current, total)

    Returns:
        List of results from all batches
    """
    results = []
    total_items = len(items)

    for i in range(0, total_items, batch_size):
        batch = items[i : i + batch_size]

        if progress_callback:
            progress_callback(i, total_items)

        logger.debug(f"Processing batch {i // batch_size + 1} ({len(batch)} items)")

        try:
            result = process_func(batch)
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing batch at index {i}: {e}")
            raise

    if progress_callback:
        progress_callback(total_items, total_items)

    return results


def process_points_from_api(data: list[dict[str, Any]]) -> Iterator[Any]:
    """Process points from API response, handling both regular and BACnet points.

    Args:
        data: List of point dictionaries from API

    Yields:
        Point instances based on data
    """
    from aceiot_models import Point

    for api_point in data:
        try:
            # Convert to Point model
            # Note: The Point model from aceiot_models handles BACnet data internally
            yield Point(**api_point)
        except Exception:
            # If model creation fails, yield the raw dict
            yield api_point


def convert_api_response_to_points(api_response: dict[str, Any]) -> dict[str, Any]:
    """Convert API response with point items to use Point models.

    Args:
        api_response: API response with 'items' key containing point data

    Returns:
        Modified response with Point objects in items
    """
    if "items" in api_response:
        api_response["items"] = list(process_points_from_api(api_response["items"]))
    return api_response


def convert_samples_to_models(samples: list[dict[str, Any]]) -> list[Any]:
    """Convert sample dictionaries to PointSample models.

    Args:
        samples: List of sample dictionaries

    Returns:
        List of PointSample objects or original dicts if conversion fails
    """
    from aceiot_models import PointSample

    converted_samples = []
    for sample in samples:
        try:
            # Try to convert to PointSample model
            converted_samples.append(PointSample(**sample))
        except Exception:
            # If conversion fails, keep the original dict
            converted_samples.append(sample)

    return converted_samples
