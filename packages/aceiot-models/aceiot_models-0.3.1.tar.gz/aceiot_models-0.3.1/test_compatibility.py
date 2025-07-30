#!/usr/bin/env python
"""Simple compatibility test for aceiot-models."""

import sys


def test_import():
    """Test that the package can be imported."""
    try:
        import aceiot_models

        print(f"✓ Import successful: aceiot_models v{aceiot_models.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_timezone_usage():
    """Test that timezone.utc is used instead of UTC."""
    try:
        from aceiot_models.timeseries import create_point_sample

        # Test creating a point sample
        sample = create_point_sample("test", 42.0)
        print(f"✓ Timezone test passed: {sample.time.tzinfo}")
        return True
    except Exception as e:
        print(f"✗ Timezone test failed: {e}")
        return False


def test_generic_syntax():
    """Test that generic syntax works."""
    try:
        from aceiot_models.clients import Client
        from aceiot_models.common import PaginatedResponse

        # Test creating a paginated response
        _ = PaginatedResponse[Client](page=1, pages=1, per_page=10, total=1, items=[])
        print("✓ Generic syntax test passed")
        return True
    except Exception as e:
        print(f"✗ Generic syntax test failed: {e}")
        return False


def main():
    """Run all tests."""
    print(f"Testing aceiot-models with Python {sys.version}")
    print("=" * 60)

    tests = [
        ("Import Test", test_import),
        ("Timezone Test", test_timezone_usage),
        ("Generic Syntax Test", test_generic_syntax),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
