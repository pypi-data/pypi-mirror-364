"""ACE IoT Models API Client Package.

This package provides a Python SDK for interacting with the ACE IoT API.
It includes a comprehensive API client, utilities for pagination and batch processing,
and helpers for data transformation.
"""

from .client import APIClient, APIError
from .pagination import PaginatedResults
from .utils import (
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


__all__ = [
    "APIClient",
    "APIError",
    "PaginatedResults",
    "batch_process",
    "convert_api_response_to_points",
    "convert_samples_to_models",
    "extract_point_paths",
    "filter_points_by_type",
    "get_api_results_paginated",
    "group_points_by_site",
    "prepare_point_for_creation",
    "process_points_from_api",
]
