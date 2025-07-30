#!/usr/bin/env python3
"""Example usage of the ACE IoT API Client.

This script demonstrates various ways to use the aceiot_models.api package
for interacting with the ACE IoT API.
"""

from datetime import datetime, timedelta

from aceiot_models.api import (
    APIClient,
    APIError,
    PaginatedResults,
    batch_process,
    get_api_results_paginated,
)
from aceiot_models.points import PointCreate


def main():
    """Run example API operations."""
    # Initialize the API client
    # You can set these via environment variables:
    # - ACEIOT_API_URL
    # - ACEIOT_API_KEY
    # - ACEIOT_API_TIMEOUT

    client = APIClient(
        base_url="https://flightdeck.aceiot.cloud/api",
        api_key="your-api-key-here",  # Replace with actual API key
        timeout=30,
    )

    print("ACE IoT API Client Examples")
    print("=" * 50)

    # Example 1: Get all clients
    print("\n1. Fetching clients...")
    try:
        clients = client.get_clients(page=1, per_page=10)
        print(f"Found {clients.get('total_items', 0)} clients")
        for client_data in clients.get("items", [])[:3]:  # Show first 3
            print(f"  - {client_data.get('name')} (ID: {client_data.get('id')})")
    except APIError as e:
        print(f"Error fetching clients: {e}")
        print(f"Status code: {e.status_code}")

    # Example 2: Using pagination
    print("\n2. Using pagination to fetch all sites...")
    try:
        paginator = PaginatedResults(client.get_sites, per_page=50)

        # Option A: Iterate page by page
        for page_sites in paginator:
            print(f"  Processing {len(page_sites)} sites...")
            # Process each page of sites

        # Option B: Get all items at once
        all_sites = paginator.all_items()
        print(f"Total sites: {len(all_sites)}")
    except APIError as e:
        print(f"Error fetching sites: {e}")

    # Example 3: Create points in batches
    print("\n3. Creating points in batches...")

    # Generate sample points
    new_points = []
    for i in range(250):  # Create 250 points
        point = PointCreate(
            name=f"sensor/temperature/{i}",
            site_id=1,  # Replace with actual site ID
            client_id=1,  # Replace with actual client ID
            point_type="analog",
            collect_enabled=True,
            collect_interval=300,  # 5 minutes
            marker_tags=["temperature", "hvac"],
            kv_tags={"unit": "celsius", "location": f"zone-{i % 10}"},
        )
        new_points.append(point.model_dump(exclude_none=True))

    # Process in batches of 100
    def create_points_batch(points_batch):
        """Create a batch of points."""
        try:
            result = client.create_points(points_batch)
            return len(result.get("items", []))
        except APIError as e:
            print(f"  Error creating batch: {e}")
            return 0

    print("Creating points in batches of 100...")
    results = batch_process(
        items=new_points,
        process_func=create_points_batch,
        batch_size=100,
        progress_callback=lambda current, total: print(f"  Progress: {current}/{total}"),
    )

    total_created = sum(results)
    print(f"Successfully created {total_created} points")

    # Example 4: Get paginated results with helper
    print("\n4. Using pagination helper to fetch points...")
    try:
        # Get all points for a specific site
        all_points = get_api_results_paginated(
            client.get_points,
            per_page=500,
            site_id=1,  # Filter by site
            max_items=1000,  # Limit to 1000 points
        )
        print(f"Fetched {len(all_points)} points")

        # Group points by type
        points_by_type = {}
        for point in all_points:
            point_type = point.get("point_type", "unknown")
            if point_type not in points_by_type:
                points_by_type[point_type] = []
            points_by_type[point_type].append(point)

        print("Points by type:")
        for ptype, points in points_by_type.items():
            print(f"  - {ptype}: {len(points)} points")
    except APIError as e:
        print(f"Error fetching points: {e}")

    # Example 5: Upload Volttron agent package with progress
    print("\n5. Uploading Volttron agent package...")

    def upload_progress(bytes_read, total_bytes):
        """Display upload progress."""
        percent = (bytes_read / total_bytes) * 100
        print(f"  Upload progress: {percent:.1f}%", end="\r")

    # Uncomment to test with actual file
    # try:
    #     result = client.upload_volttron_agent_package(
    #         gateway_name="gateway-1",
    #         file_path="/path/to/agent.tar.gz",
    #         package_name="my-custom-agent",
    #         description="Custom analytics agent",
    #         progress_callback=upload_progress
    #     )
    #     print(f"\nUpload complete: {result}")
    # except APIError as e:
    #     print(f"Error uploading package: {e}")

    # Example 6: Get time series data
    print("\n6. Fetching time series data...")
    try:
        # Get samples for the last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)

        samples = client.get_samples(
            point_ids=[1, 2, 3],  # Replace with actual point IDs
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            limit=1000,
        )

        print(f"Fetched {len(samples.get('items', []))} samples")
    except APIError as e:
        print(f"Error fetching samples: {e}")

    # Example 7: Error handling patterns
    print("\n7. Error handling examples...")

    try:
        # This will fail with 404
        client.get_site(99999)
    except APIError as e:
        print(f"Expected error: {e}")
        if e.status_code == 404:
            print("  Site not found (404)")
        elif e.status_code == 401:
            print("  Authentication failed - check API key")
        elif e.status_code == 403:
            print("  Permission denied")
        elif e.status_code == 429:
            print("  Rate limit exceeded - slow down requests")
        else:
            print(f"  Unexpected error: {e.status_code}")

    print("\n" + "=" * 50)
    print("Examples complete!")


if __name__ == "__main__":
    # Set environment variables or update the API key above
    # os.environ["ACEIOT_API_KEY"] = "your-api-key"
    main()
