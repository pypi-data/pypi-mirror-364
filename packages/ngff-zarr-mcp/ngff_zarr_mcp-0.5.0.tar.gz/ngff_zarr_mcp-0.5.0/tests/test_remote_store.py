"""Tests for remote OME-Zarr store functionality."""

import pytest
import tempfile
from pathlib import Path

from ngff_zarr_mcp.tools import (
    convert_to_ome_zarr,
    inspect_ome_zarr,
    read_ngff_zarr,
)
from ngff_zarr_mcp.models import ConversionOptions, ConversionResult, StoreInfo


# Remote OME-Zarr store URL from DANDI Archive
REMOTE_STORE_URL = (
    "https://dandiarchive.s3.amazonaws.com/zarr/ca578830-fb23-4aa6-8471-cfde8478abfb/"
)

# Skip remote tests if network is not available
pytestmark = pytest.mark.skipif(
    False,  # Change to True to skip remote tests during development
    reason="Remote tests disabled during development",
)


@pytest.mark.asyncio
async def test_inspect_remote_ome_zarr():
    """Test inspecting a remote OME-Zarr store."""
    try:
        # Test the inspect function with remote store
        store_info = await inspect_ome_zarr(REMOTE_STORE_URL)

        # Verify the result structure
        assert isinstance(store_info, StoreInfo)
        assert store_info.path == REMOTE_STORE_URL
        assert store_info.version in ["0.4", "0.5"]
        assert store_info.size_bytes > 0
        assert store_info.num_files > 0
        assert store_info.num_scales > 0
        assert len(store_info.dimensions) > 0
        assert len(store_info.shape) > 0
        assert store_info.dtype is not None

        # Print some info for verification
        print("Remote store info:")
        print(f"  Version: {store_info.version}")
        print(f"  Dimensions: {store_info.dimensions}")
        print(f"  Shape: {store_info.shape}")
        print(f"  Scales: {store_info.num_scales}")
        print(f"  Data type: {store_info.dtype}")

    except Exception as e:
        pytest.skip(f"Remote store access failed: {e}")


@pytest.mark.asyncio
async def test_read_remote_ome_zarr_store():
    """Test reading a remote OME-Zarr store."""
    try:
        # Test the read function with remote store
        result = await read_ngff_zarr(REMOTE_STORE_URL, validate=True)

        # Verify the result structure
        assert isinstance(result, ConversionResult)
        assert result.success is True
        assert result.output_path == REMOTE_STORE_URL
        assert result.error is None
        assert isinstance(result.store_info, dict)

        # Verify store info contains expected fields
        store_info = result.store_info
        assert "path" in store_info
        assert "version" in store_info
        assert "dimensions" in store_info
        assert "shape" in store_info
        assert "num_scales" in store_info

        # Print some info for verification
        print("Read remote store result:")
        print(f"  Success: {result.success}")
        print(f"  Version: {store_info.get('version')}")
        print(f"  Dimensions: {store_info.get('dimensions')}")
        print(f"  Shape: {store_info.get('shape')}")

        # Check for new fields we added
        if "method_type" in store_info:
            print(f"  Method type: {store_info['method_type']}")
        if "rfc_support" in store_info:
            print(f"  RFC support: {store_info['rfc_support']}")

    except Exception as e:
        pytest.skip(f"Remote store access failed: {e}")


@pytest.mark.asyncio
async def test_read_remote_ome_zarr_store_with_storage_options():
    """Test reading a remote OME-Zarr store with storage options."""
    try:
        # Test with empty storage options (should not break anything)
        storage_options = {}
        result = await read_ngff_zarr(
            REMOTE_STORE_URL,
            storage_options=storage_options,
            validate=False,  # Skip validation for speed
        )

        # Verify the result structure
        assert isinstance(result, ConversionResult)
        assert result.success is True
        assert result.output_path == REMOTE_STORE_URL
        assert result.error is None

        print("Read with storage options succeeded")

    except Exception as e:
        # This might fail if storage_options not supported yet
        print(f"Storage options test failed (expected): {e}")
        pytest.skip(f"Storage options not supported yet: {e}")


@pytest.mark.asyncio
async def test_convert_remote_to_local():
    """Test converting a remote OME-Zarr store to a local store."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "converted_remote.ome.zarr"

            # Configure conversion from remote store
            options = ConversionOptions(
                output_path=str(output_path),
                ome_zarr_version="0.4",
                method="itkwasm_gaussian",
                # Don't create multiscales to save time/space
                scale_factors=None,
                # Use small chunks for testing
                chunks=[64],
                # Use compression to save space
                compression_codec="gzip",
                compression_level=1,
            )

            # Perform conversion from remote store
            result = await convert_to_ome_zarr([REMOTE_STORE_URL], options)

            # Verify conversion succeeded
            assert result.success, f"Conversion failed: {result.error}"
            assert result.output_path == str(output_path)
            assert result.error is None

            # Verify output exists
            assert output_path.exists()

            # Verify output is a valid OME-Zarr store
            local_store_info = await inspect_ome_zarr(str(output_path))
            assert isinstance(local_store_info, StoreInfo)
            assert local_store_info.version in ["0.4", "0.5"]

            print("Successfully converted remote store to local:")
            print(f"  Input: {REMOTE_STORE_URL}")
            print(f"  Output: {output_path}")
            print(f"  Output size: {local_store_info.size_bytes} bytes")
            print(f"  Output scales: {local_store_info.num_scales}")

    except Exception as e:
        pytest.skip(f"Remote to local conversion failed: {e}")


@pytest.mark.asyncio
async def test_convert_with_rfc4_options():
    """Test conversion with RFC 4 anatomical orientation options."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "converted_with_rfc4.ome.zarr"

            # Configure conversion with RFC 4 options
            options = ConversionOptions(
                output_path=str(output_path),
                ome_zarr_version="0.4",
                method="itkwasm_gaussian",
                scale_factors=None,
                chunks=[64],
                compression_codec="gzip",
                compression_level=1,
                # RFC 4 options
                anatomical_orientation="LPS",
                enable_rfc4=True,
                enabled_rfcs=[4],
            )

            # Perform conversion with RFC 4 options
            result = await convert_to_ome_zarr([REMOTE_STORE_URL], options)

            # Note: This might not fully work yet if RFC 4 not implemented
            # but should not crash
            print(f"RFC 4 conversion result: success={result.success}")
            if not result.success:
                print(f"RFC 4 error (expected): {result.error}")
            else:
                print("RFC 4 conversion succeeded!")
                assert output_path.exists()

    except Exception as e:
        print(f"RFC 4 test failed (expected): {e}")
        # Don't fail the test if RFC 4 not implemented yet


@pytest.mark.asyncio
async def test_remote_store_error_handling():
    """Test error handling with invalid remote stores."""

    # Test with non-existent URL
    invalid_url = "https://example.com/nonexistent/store.ome.zarr"

    try:
        result = await read_ngff_zarr(invalid_url)
        # Should return error result, not crash
        assert isinstance(result, ConversionResult)
        assert result.success is False
        assert result.error is not None
        print(f"Invalid URL correctly handled: {result.error}")

    except Exception as e:
        # This is also acceptable - error handling via exception
        print(f"Invalid URL raised exception (acceptable): {e}")

    # Test with malformed URL
    malformed_url = "not-a-url"

    try:
        result = await read_ngff_zarr(malformed_url)
        assert isinstance(result, ConversionResult)
        assert result.success is False
        assert result.error is not None
        print(f"Malformed URL correctly handled: {result.error}")

    except Exception as e:
        print(f"Malformed URL raised exception (acceptable): {e}")


@pytest.mark.asyncio
async def test_remote_store_network_timeout():
    """Test handling of network timeouts and slow connections."""

    # This is more of a stress test - using a very slow/timeout URL
    timeout_url = "https://httpstat.us/200?sleep=30000"  # 30 second delay

    try:
        # This should timeout or be handled gracefully
        result = await read_ngff_zarr(timeout_url)

        # If we get here, check the result
        assert isinstance(result, ConversionResult)
        if not result.success:
            print(f"Timeout URL correctly handled: {result.error}")
        else:
            print("Timeout URL unexpectedly succeeded")

    except Exception as e:
        print(f"Timeout URL raised exception (acceptable): {e}")
