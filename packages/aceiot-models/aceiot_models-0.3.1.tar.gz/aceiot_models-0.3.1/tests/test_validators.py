"""Tests for the validator functions."""

import pytest

from aceiot_models.validators import (
    validate_coordinate,
    validate_coordinate_pair,
    validate_email,
    validate_hierarchy,
    validate_mac_address,
    validate_name,
    validate_positive_integer,
    validate_string_length,
    validate_unique_in_list,
    validate_url,
)


class TestValidatorFunctions:
    """Test the validator functions."""

    def test_validate_name(self):
        """Test name validation."""
        # Valid names
        assert validate_name("Valid Name") == "Valid Name"
        assert validate_name("  Trimmed  ") == "Trimmed"

        # Invalid names
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_name("")

        with pytest.raises(ValueError, match="at least 2 characters"):
            validate_name("a")

    def test_validate_mac_address(self):
        """Test MAC address validation."""
        # Valid MAC addresses
        assert validate_mac_address("00:11:22:33:44:55") == "00:11:22:33:44:55"
        assert validate_mac_address("001122334455") == "001122334455"
        assert validate_mac_address(None) is None

        # Invalid MAC
        with pytest.raises(ValueError, match="Invalid MAC address"):
            validate_mac_address("invalid-mac")

    def test_validate_coordinate(self):
        """Test coordinate validation."""
        # Valid coordinates
        assert validate_coordinate(40.7128, "latitude") == 40.7128
        assert validate_coordinate(-74.0060, "longitude") == -74.0060
        assert validate_coordinate(None) is None

        # Invalid coordinates
        with pytest.raises(ValueError, match="between -90 and 90"):
            validate_coordinate(91, "latitude")

    def test_validate_positive_integer(self):
        """Test positive integer validation."""
        assert validate_positive_integer(0) == 0
        assert validate_positive_integer(100) == 100
        assert validate_positive_integer(None) is None

        with pytest.raises(ValueError, match="non-negative"):
            validate_positive_integer(-1)

    def test_validate_string_length(self):
        """Test string length validation."""
        # Valid strings
        assert validate_string_length("Valid text", min_length=5, max_length=20) == "Valid text"
        assert validate_string_length("", allow_empty_as_none=True) is None

        # Invalid lengths
        with pytest.raises(ValueError, match="at least 5 characters"):
            validate_string_length("abc", min_length=5, allow_empty_as_none=False)

    def test_validate_email(self):
        """Test email validation."""
        assert validate_email("test@example.com") == "test@example.com"
        assert validate_email(None) is None

        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email("invalid-email")

    def test_validate_url(self):
        """Test URL validation."""
        assert validate_url("https://example.com") == "https://example.com"
        assert validate_url(None) is None

        with pytest.raises(ValueError, match="Invalid URL format"):
            validate_url("not-a-url")

    def test_validate_coordinate_pair(self):
        """Test coordinate pair validation."""
        # Valid pairs
        lat, lon = validate_coordinate_pair(40.7, -74.0)
        assert lat == 40.7 and lon == -74.0

        lat, lon = validate_coordinate_pair(None, None)
        assert lat is None and lon is None

        # Invalid pair
        with pytest.raises(ValueError, match="together"):
            validate_coordinate_pair(40.7, None)

    def test_validate_unique_in_list(self):
        """Test uniqueness validation."""
        # Unique items
        assert validate_unique_in_list([{"name": "A"}, {"name": "B"}])

        # Duplicate items
        assert not validate_unique_in_list([{"name": "A"}, {"name": "a"}], case_sensitive=False)

        # Empty list
        assert validate_unique_in_list([])

    def test_validate_hierarchy(self):
        """Test hierarchy validation."""
        existing = {1: [2, 3], 2: [4, 5]}

        # Valid hierarchy
        assert validate_hierarchy(6, [7, 8], existing)

        # Self-reference
        with pytest.raises(ValueError, match="circular reference"):
            validate_hierarchy(1, [1, 2], existing)
