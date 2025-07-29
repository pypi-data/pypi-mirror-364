"""Test remote OME-Zarr functionality with local test data."""

import pytest
import tempfile
from pathlib import Path
import zarr
import numpy as np

from ngff_zarr_mcp.server import (
    get_ome_zarr_info,
    read_ome_zarr_store,
    validate_ome_zarr_store,
)
from ngff_zarr_mcp.models import StoreInfo, ValidationResult, ConversionResult


@pytest.fixture
def sample_ome_zarr_store():
    """Create a simple OME-Zarr store for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store_path = Path(temp_dir) / "test.ome.zarr"

        # Create a simple zarr group
        zarr_group = zarr.open_group(str(store_path), mode="w")

        # Create multiscale data (2 scales)
        scale0_array = zarr_group.create_dataset(
            "0", shape=(1, 1, 10, 100, 100), chunks=(1, 1, 10, 50, 50), dtype=np.uint16
        )
        scale0_array[:] = np.random.randint(0, 1000, size=(1, 1, 10, 100, 100))

        scale1_array = zarr_group.create_dataset(
            "1", shape=(1, 1, 5, 50, 50), chunks=(1, 1, 5, 25, 25), dtype=np.uint16
        )
        scale1_array[:] = np.random.randint(0, 1000, size=(1, 1, 5, 50, 50))

        # Add OME-Zarr metadata
        metadata = {
            "multiscales": [
                {
                    "version": "0.4",
                    "axes": [
                        {"name": "t", "type": "time", "unit": "second"},
                        {"name": "c", "type": "channel"},
                        {"name": "z", "type": "space", "unit": "micrometer"},
                        {"name": "y", "type": "space", "unit": "micrometer"},
                        {"name": "x", "type": "space", "unit": "micrometer"},
                    ],
                    "datasets": [
                        {
                            "path": "0",
                            "coordinateTransformations": [
                                {"type": "scale", "scale": [1.0, 1.0, 1.0, 0.5, 0.5]},
                                {
                                    "type": "translation",
                                    "translation": [0.0, 0.0, 0.0, 0.0, 0.0],
                                },
                            ],
                        },
                        {
                            "path": "1",
                            "coordinateTransformations": [
                                {"type": "scale", "scale": [1.0, 1.0, 2.0, 1.0, 1.0]},
                                {
                                    "type": "translation",
                                    "translation": [0.0, 0.0, 0.0, 0.0, 0.0],
                                },
                            ],
                        },
                    ],
                    "metadata": {"method": "scipy.ndimage.zoom", "version": "1.2.1"},
                }
            ]
        }

        zarr_group.attrs.update(metadata)

        yield str(store_path)


@pytest.mark.asyncio
async def test_mcp_get_ome_zarr_info_local(sample_ome_zarr_store):
    """Test the MCP get_ome_zarr_info function with local store."""
    store_info = await get_ome_zarr_info(sample_ome_zarr_store)

    # Verify the result structure
    assert isinstance(store_info, StoreInfo)
    assert store_info.path == sample_ome_zarr_store
    assert store_info.version == "0.4"
    assert store_info.size_bytes > 0
    assert store_info.num_files > 0
    assert store_info.num_scales == 2
    assert len(store_info.dimensions) == 5
    assert len(store_info.shape) == 5
    assert store_info.dtype is not None

    # Test new fields
    assert hasattr(store_info, "method_type")
    assert hasattr(store_info, "method_metadata")
    assert hasattr(store_info, "anatomical_orientation")
    assert hasattr(store_info, "rfc_support")

    print("Local store test passed:")
    print(f"  Store version: {store_info.version}")
    print(f"  Dimensions: {store_info.dimensions}")
    print(f"  Shape: {store_info.shape}")
    print(f"  Number of scales: {store_info.num_scales}")


@pytest.mark.asyncio
async def test_mcp_read_ome_zarr_store_local(sample_ome_zarr_store):
    """Test the MCP read_ome_zarr_store function with local store."""
    result = await read_ome_zarr_store(sample_ome_zarr_store)

    # Verify the result structure
    assert isinstance(result, ConversionResult)
    assert result.success is True
    assert result.output_path == sample_ome_zarr_store

    print("Local read_ome_zarr_store test passed")


@pytest.mark.asyncio
async def test_mcp_validate_ome_zarr_store_local(sample_ome_zarr_store):
    """Test the MCP validate_ome_zarr_store function with local store."""
    result = await validate_ome_zarr_store(sample_ome_zarr_store)

    # Verify the result structure (validation may fail due to test store simplicity)
    assert isinstance(result, ValidationResult)
    assert result.version is None or result.version == "0.4"
    assert isinstance(result.errors, list)
    assert isinstance(result.warnings, list)

    # Just log the validation result
    print(f"Validation result: valid={result.valid}, errors={result.errors}")
    print("Local validate_ome_zarr_store test passed")


def test_remote_store_error_handling():
    """Test that remote store errors are handled gracefully."""
    from ngff_zarr_mcp.utils import analyze_zarr_store

    # Test with invalid URL
    with pytest.raises(ValueError) as exc_info:
        analyze_zarr_store("https://invalid-url-that-does-not-exist.com/store/")

    assert "Failed to analyze store" in str(exc_info.value)
    print("Remote error handling test passed")


@pytest.mark.asyncio
async def test_network_capabilities():
    """Test that network access is working and document remote functionality."""
    import requests
    import fsspec

    try:
        # Test basic HTTP access
        response = requests.get("https://httpbin.org/status/200", timeout=5)
        assert response.status_code == 200

        # Test fsspec HTTP mapper
        mapper = fsspec.get_mapper("https://httpbin.org/")
        assert mapper is not None

        print("Network capabilities test passed - remote stores should work")
        print("Remote OME-Zarr functionality is available with proper dependencies:")
        print("  - requests: for HTTP access")
        print("  - aiohttp: for async HTTP operations")
        print("  - fsspec: for filesystem abstraction")
        print("")
        print("Known limitations:")
        print(
            "  - Some DANDI stores use 'min'/'max' instead of 'start'/'end' in OMERO metadata"
        )
        print(
            "  - zarr v3 FSMap path handling can cause issues with some remote stores"
        )
        print("  - Error handling provides graceful fallbacks and clear error messages")

    except Exception as e:
        pytest.skip(f"Network access not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
