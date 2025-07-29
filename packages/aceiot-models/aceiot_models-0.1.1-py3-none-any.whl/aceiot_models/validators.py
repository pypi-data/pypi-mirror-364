"""Reusable validator functions for ACE IoT models."""

import re
from typing import Any


def validate_name(
    value: str | None,
    min_length: int = 2,
    allow_spaces: bool = True,
    strip_whitespace: bool = True,
    invalid_chars: list[str] | None = None,
) -> str | None:
    """Validate name fields with configurable options."""
    if value is None:
        return value

    if strip_whitespace:
        value = value.strip()

    if not value:
        raise ValueError("Name cannot be empty")

    if len(value) < min_length:
        raise ValueError(f"Name must be at least {min_length} characters long")

    if not allow_spaces and " " in value:
        raise ValueError("Name cannot contain spaces")

    if invalid_chars:
        found_chars = [char for char in invalid_chars if char in value]
        if found_chars:
            raise ValueError(f"Name cannot contain the following characters: {found_chars}")

    return value


def validate_mac_address(value: str | None) -> str | None:
    """Validate MAC address format."""
    if value is None:
        return value

    value = value.strip()
    if not value:
        return None

    # MAC address patterns
    mac_patterns = [
        r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",  # XX:XX:XX:XX:XX:XX
        r"^([0-9A-Fa-f]{2}){6}$",  # XXXXXXXXXXXX
        r"^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$",  # XXXX.XXXX.XXXX
    ]

    if not any(re.match(pattern, value) for pattern in mac_patterns):
        raise ValueError("Invalid MAC address format")

    return value


def validate_coordinate(value: float | None, coord_type: str = "latitude") -> float | None:
    """Validate geographic coordinates."""
    if value is None:
        return value

    if coord_type == "latitude":
        min_val, max_val = -90, 90
    elif coord_type == "longitude":
        min_val, max_val = -180, 180
    else:
        raise ValueError(f"Invalid coordinate type: {coord_type}")

    if value < min_val or value > max_val:
        raise ValueError(
            f"{coord_type.capitalize()} must be between {min_val} and {max_val} degrees"
        )
    return value


def validate_positive_integer(value: int | None, field_name: str = "value") -> int | None:
    """Validate positive integer values."""
    if value is None:
        return value

    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")
    return value


def validate_string_length(
    value: str | None,
    min_length: int | None = None,
    max_length: int | None = None,
    strip_whitespace: bool = True,
    allow_empty_as_none: bool = True,
) -> str | None:
    """Validate string length constraints."""
    if value is None:
        return value

    if strip_whitespace:
        value = value.strip()

    # Convert empty strings to None if allowed
    if allow_empty_as_none and not value:
        return None

    if min_length is not None and len(value) < min_length:
        raise ValueError(f"Must be at least {min_length} characters long")

    if max_length is not None and len(value) > max_length:
        raise ValueError(f"Cannot exceed {max_length} characters")

    return value


def validate_email(value: str | None) -> str | None:
    """Validate email format."""
    if value is None:
        return value

    # Simple email regex - for production use email-validator library
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    value = value.strip().lower()
    if not re.match(email_pattern, value):
        raise ValueError("Invalid email format")

    return value


def validate_url(value: str | None, require_https: bool = False) -> str | None:
    """Validate URL format."""
    if value is None:
        return value

    value = value.strip()
    url_pattern = (
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$"
    )

    if not re.match(url_pattern, value, re.IGNORECASE):
        raise ValueError("Invalid URL format")

    if require_https and not value.startswith("https://"):
        raise ValueError("URL must use HTTPS protocol")

    return value


def validate_coordinate_pair(
    latitude: float | None, longitude: float | None
) -> tuple[float | None, float | None]:
    """Validate that latitude and longitude are provided together."""
    if (latitude is None) != (longitude is None):
        raise ValueError(
            "Both latitude and longitude must be provided together, or both should be None"
        )
    return latitude, longitude


def validate_unique_in_list(
    items: list[Any], field: str = "name", case_sensitive: bool = False
) -> bool:
    """Validate that all items in a list have unique values for a field."""
    if not items:
        return True

    values = []
    for item in items:
        value = getattr(item, field, None) if hasattr(item, field) else item.get(field)
        if value is not None:
            if not case_sensitive and isinstance(value, str):
                value = value.lower()
            values.append(value)

    return len(values) == len(set(values))


def validate_hierarchy(
    parent_id: int | None, child_ids: list[int], existing_hierarchy: dict[int, list[int]]
) -> bool:
    """Validate that there are no circular references in hierarchy."""
    if parent_id is None:
        return True

    # Check for self-reference
    if parent_id in child_ids:
        raise ValueError("Cannot create circular reference: parent cannot be its own child")

    # Check for circular references in hierarchy
    visited = set()
    queue = [parent_id]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue

        visited.add(current)
        if current in child_ids:
            raise ValueError(f"Circular reference detected: {current} is both parent and child")

        # Add children of current node to queue
        queue.extend(existing_hierarchy.get(current, []))

    return True


def validate_non_empty_string(value: str | None, field_name: str = "value") -> str | None:
    """Validate that a string is not empty after stripping whitespace.

    Args:
        value: The string value to validate
        field_name: Name of the field for error messages

    Returns:
        The stripped string value

    Raises:
        ValueError: If the string is empty or only whitespace
    """
    if value is None:
        return value

    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty")

    return value


def validate_integer_range(
    value: int | None,
    field_name: str = "value",
    min_value: int | None = None,
    max_value: int | None = None,
) -> int | None:
    """Validate that an integer is within the specified range.

    Args:
        value: The integer value to validate
        field_name: Name of the field for error messages
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Returns:
        The validated integer value

    Raises:
        ValueError: If the value is outside the specified range
    """
    if value is None:
        return value

    if min_value is not None and value < min_value:
        if max_value is not None:
            raise ValueError(f"{field_name} must be between {min_value} and {max_value}")
        else:
            raise ValueError(f"{field_name} must be at least {min_value}")

    if max_value is not None and value > max_value:
        if min_value is not None:
            raise ValueError(f"{field_name} must be between {min_value} and {max_value}")
        else:
            raise ValueError(f"{field_name} must be at most {max_value}")

    return value


def validate_float(value: float | None, field_name: str = "value") -> float | None:
    """Validate that a value is a valid float.

    Args:
        value: The float value to validate
        field_name: Name of the field for error messages

    Returns:
        The validated float value

    Raises:
        ValueError: If the value is not a valid float (e.g., NaN or infinity)
    """
    if value is None:
        return value

    # Convert int to float if needed
    if isinstance(value, int):
        value = float(value)

    # Check for special float values
    if isinstance(value, float):
        import math

        if math.isnan(value):
            raise ValueError(f"{field_name} cannot be NaN")
        if math.isinf(value):
            raise ValueError(f"{field_name} cannot be infinity")

    return value


# Export all validators
__all__ = [
    "validate_coordinate",
    "validate_coordinate_pair",
    "validate_email",
    "validate_float",
    "validate_hierarchy",
    "validate_integer_range",
    "validate_mac_address",
    "validate_name",
    "validate_non_empty_string",
    "validate_positive_integer",
    "validate_string_length",
    "validate_unique_in_list",
    "validate_url",
]
