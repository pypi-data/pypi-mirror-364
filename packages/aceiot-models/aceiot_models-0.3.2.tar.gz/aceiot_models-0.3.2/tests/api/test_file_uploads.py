"""Test file upload functionality in API client."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from aceiot_models.api import APIClient


class TestFileUploads:
    """Test file upload methods with proper MIME types."""

    @pytest.fixture
    def api_client(self):
        """Create API client with mocked request method."""
        client = APIClient(api_key="test-key")
        client._request = MagicMock(return_value={"success": True})
        return client

    def test_volttron_package_upload_whl(self, api_client):
        """Test uploading a .whl file with correct MIME type."""
        with tempfile.NamedTemporaryFile(suffix=".whl", delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(b"fake wheel content")

        try:
            api_client.upload_client_volttron_agent_package(
                client_name="test-client",
                file_path=tmp_path,
                package_name="test-package",
                description="Test package",
            )

            # Check that _request was called with correct parameters
            api_client._request.assert_called_once()
            call_args = api_client._request.call_args

            # Verify files parameter structure
            files_arg = call_args.kwargs["files"]
            assert "file" in files_arg
            filename, file_obj, mime_type = files_arg["file"]
            assert filename.endswith(".whl")
            assert mime_type == "application/zip"

            # Verify Content-Type header is not set (so requests can set multipart/form-data)
            headers = call_args.kwargs.get("headers", {})
            assert (
                "Content-Type" not in headers or headers.get("Content-Type") != "application/json"
            )

        finally:
            Path(tmp_path).unlink()

    def test_volttron_package_upload_tar_gz(self, api_client):
        """Test uploading a .tar.gz file with correct MIME type."""
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(b"fake tarball content")

        try:
            api_client.upload_client_volttron_agent_package(
                client_name="test-client", file_path=tmp_path, package_name="test-package"
            )

            # Check MIME type
            call_args = api_client._request.call_args
            files_arg = call_args.kwargs["files"]
            _, _, mime_type = files_arg["file"]
            # mimetypes.guess_type returns 'application/x-tar' for .tar.gz
            assert mime_type in ["application/x-gzip", "application/x-tar"]

        finally:
            Path(tmp_path).unlink()

    def test_pcap_upload(self, api_client):
        """Test uploading a PCAP file with correct MIME type."""
        with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(b"fake pcap content")

        try:
            api_client.upload_gateway_pcap(gateway_name="test-gateway", file_path=tmp_path)

            # Check MIME type
            call_args = api_client._request.call_args
            files_arg = call_args.kwargs["files"]
            _, _, mime_type = files_arg["file"]
            assert mime_type == "application/vnd.tcpdump.pcap"

        finally:
            Path(tmp_path).unlink()

    def test_unknown_file_type(self, api_client):
        """Test uploading unknown file type defaults to octet-stream."""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(b"unknown content")

        try:
            api_client.upload_client_volttron_agent_package(
                client_name="test-client", file_path=tmp_path, package_name="test-package"
            )

            # Check MIME type
            call_args = api_client._request.call_args
            files_arg = call_args.kwargs["files"]
            _, _, mime_type = files_arg["file"]
            # Should fall back to octet-stream or use mimetypes result
            assert mime_type in ["application/octet-stream", "chemical/x-xyz"]

        finally:
            Path(tmp_path).unlink()
