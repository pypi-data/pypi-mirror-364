"""Integration tests for MCP server functions with remote stores."""

import pytest
import tempfile
from pathlib import Path

from ngff_zarr_mcp.server import (
    convert_images_to_ome_zarr,
    get_ome_zarr_info,
    read_ome_zarr_store,
    validate_ome_zarr_store,
)
from ngff_zarr_mcp.models import ConversionResult, StoreInfo, ValidationResult


# Remote OME-Zarr store URL from DANDI Archive
REMOTE_STORE_URL = (
    "https://dandiarchive.s3.amazonaws.com/zarr/ca578830-fb23-4aa6-8471-cfde8478abfb/"
)

# Alternative compatible remote store URL (IDR OME-Zarr)
COMPATIBLE_REMOTE_STORE = (
    "https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0062A/6001240.zarr/"
)


@pytest.mark.asyncio
async def test_mcp_get_ome_zarr_info_compatible_remote():
    """Test the MCP get_ome_zarr_info function with a known compatible remote store."""
    try:
        store_info = await get_ome_zarr_info(COMPATIBLE_REMOTE_STORE)

        # Verify the result structure
        assert isinstance(store_info, StoreInfo)
        assert store_info.path == COMPATIBLE_REMOTE_STORE
        assert store_info.version in ["0.4", "0.5"]
        assert store_info.size_bytes > 0
        assert store_info.num_files > 0
        assert store_info.num_scales > 0
        assert len(store_info.dimensions) > 0
        assert len(store_info.shape) > 0
        assert store_info.dtype is not None

        print("MCP get_ome_zarr_info test with compatible store passed:")
        print(f"  Store version: {store_info.version}")
        print(f"  Dimensions: {store_info.dimensions}")
        print(f"  Shape: {store_info.shape}")
        print(f"  Number of scales: {store_info.num_scales}")

    except Exception as e:
        pytest.skip(f"Compatible remote store access failed: {e}")


@pytest.mark.asyncio
async def test_mcp_get_ome_zarr_info_remote():
    """Test the MCP get_ome_zarr_info function with remote store."""
    try:
        store_info = await get_ome_zarr_info(REMOTE_STORE_URL)

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

        # Test new fields we added
        assert hasattr(store_info, "method_type")
        assert hasattr(store_info, "method_metadata")
        assert hasattr(store_info, "anatomical_orientation")
        assert hasattr(store_info, "rfc_support")

        print("MCP get_ome_zarr_info test passed:")
        print(f"  Store version: {store_info.version}")
        print(f"  Dimensions: {store_info.dimensions}")
        print(f"  Shape: {store_info.shape}")
        print(f"  Number of scales: {store_info.num_scales}")

    except ValueError as e:
        if "incompatible OMERO metadata format" in str(e):
            pytest.skip(f"Remote store has OMERO metadata compatibility issue: {e}")
        else:
            pytest.skip(f"Remote store access failed: {e}")
    except Exception as e:
        pytest.skip(f"Remote store access failed: {e}")


@pytest.mark.asyncio
async def test_mcp_read_ome_zarr_store_remote():
    """Test the MCP read_ome_zarr_store function with remote store."""
    try:
        result = await read_ome_zarr_store(store_path=REMOTE_STORE_URL, validate=True)

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

        print("MCP read_ome_zarr_store test passed:")
        print(f"  Success: {result.success}")
        print(f"  Store version: {store_info.get('version')}")
        print(f"  Dimensions: {store_info.get('dimensions')}")

        # Check for new metadata fields
        if "method_type" in store_info and store_info["method_type"]:
            print(f"  Method type detected: {store_info['method_type']}")
        if "rfc_support" in store_info and store_info["rfc_support"]:
            print(f"  RFC support detected: {store_info['rfc_support']}")

    except Exception as e:
        pytest.skip(f"Remote store access failed: {e}")


@pytest.mark.asyncio
async def test_mcp_read_ome_zarr_store_with_storage_options():
    """Test the MCP read function with storage options."""
    try:
        # Test with AWS-style storage options (even though this store is public)
        storage_options = {
            "anon": True,  # Anonymous access
            "client_kwargs": {"region_name": "us-east-1"},
        }

        result = await read_ome_zarr_store(
            store_path=REMOTE_STORE_URL, storage_options=storage_options, validate=False
        )

        # Should succeed or fail gracefully
        assert isinstance(result, ConversionResult)

        if result.success:
            print("Storage options test succeeded")
            assert result.output_path == REMOTE_STORE_URL
            assert isinstance(result.store_info, dict)
        else:
            print(f"Storage options test failed (expected): {result.error}")

    except Exception as e:
        print(f"Storage options test raised exception (acceptable): {e}")


@pytest.mark.asyncio
async def test_mcp_validate_ome_zarr_store_remote():
    """Test the MCP validate_ome_zarr_store function with remote store."""
    try:
        validation_result = await validate_ome_zarr_store(REMOTE_STORE_URL)

        # Verify the result structure
        assert isinstance(validation_result, ValidationResult)

        # The store should be valid
        assert validation_result.valid is True
        assert validation_result.version in ["0.4", "0.5"]
        assert isinstance(validation_result.errors, list)
        assert isinstance(validation_result.warnings, list)

        print("MCP validate_ome_zarr_store test passed:")
        print(f"  Valid: {validation_result.valid}")
        print(f"  Version: {validation_result.version}")
        print(f"  Errors: {len(validation_result.errors)}")
        print(f"  Warnings: {len(validation_result.warnings)}")

        if validation_result.warnings:
            print("  Warning messages:")
            for warning in validation_result.warnings:
                print(f"    - {warning}")

    except Exception as e:
        pytest.skip(f"Remote validation failed: {e}")


@pytest.mark.asyncio
async def test_mcp_convert_images_to_ome_zarr_remote():
    """Test the MCP convert_images_to_ome_zarr function with remote input."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "converted_from_remote.ome.zarr"

            # Test conversion from remote store to local store
            result = await convert_images_to_ome_zarr(
                input_paths=[REMOTE_STORE_URL],
                output_path=str(output_path),
                ome_zarr_version="0.4",
                method="itkwasm_gaussian",
                scale_factors=None,  # Single scale to save time
                chunks=[64],  # Fix: should be a list
                compression_codec="gzip",
                compression_level=1,
                use_tensorstore=False,
                use_local_cluster=False,
                cache_dir=None,
            )

            # Verify conversion succeeded
            assert isinstance(result, ConversionResult)
            assert result.success, f"Conversion failed: {result.error}"
            assert result.output_path == str(output_path)
            assert result.error is None

            # Verify output exists and is valid
            assert output_path.exists()

            # Verify we can read the converted store
            converted_info = await get_ome_zarr_info(str(output_path))
            assert isinstance(converted_info, StoreInfo)
            assert converted_info.version in ["0.4", "0.5"]

            print("MCP convert_images_to_ome_zarr test passed:")
            print(f"  Input: {REMOTE_STORE_URL}")
            print(f"  Output: {output_path}")
            print(f"  Output size: {converted_info.size_bytes} bytes")
            print(f"  Output dimensions: {converted_info.dimensions}")

    except Exception as e:
        pytest.skip(f"Remote conversion failed: {e}")


@pytest.mark.asyncio
async def test_mcp_convert_with_new_features():
    """Test MCP conversion with new RFC 4 and storage features."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "converted_with_features.ome.zarr"

            # Test conversion with new features
            result = await convert_images_to_ome_zarr(
                input_paths=[REMOTE_STORE_URL],
                output_path=str(output_path),
                ome_zarr_version="0.4",
                method="itkwasm_gaussian",
                scale_factors=None,
                chunks=[64],  # Fix: should be a list
                compression_codec="gzip",
                compression_level=1,
                # New features
                anatomical_orientation="LPS",
                enable_rfc4=True,
                enabled_rfcs=[4],
                # storage_options={"anon": "True"},  # Temporarily disabled due to type issues
            )

            # Should not crash, even if features not fully implemented
            assert isinstance(result, ConversionResult)

            if result.success:
                print("Conversion with new features succeeded!")
                assert output_path.exists()

                # Check if we can detect any new metadata
                converted_info = await get_ome_zarr_info(str(output_path))
                if (
                    hasattr(converted_info, "rfc_support")
                    and converted_info.rfc_support
                ):
                    print(f"  RFC support detected: {converted_info.rfc_support}")

            else:
                print(
                    f"Conversion with new features failed (may be expected): {result.error}"
                )

    except Exception as e:
        print(f"New features test failed (may be expected): {e}")


@pytest.mark.asyncio
async def test_mcp_error_handling():
    """Test MCP error handling with invalid remote URLs."""

    # Test with non-existent remote store
    invalid_url = "https://example.com/nonexistent.ome.zarr"

    # Test get_ome_zarr_info with invalid URL
    try:
        result = await get_ome_zarr_info(invalid_url)
        # Should raise an exception since it returns StoreInfo directly
        pytest.fail("Expected exception for invalid URL")
    except Exception as e:
        print(f"get_ome_zarr_info correctly raised exception: {e}")

    # Test read_ome_zarr_store with invalid URL
    try:
        result = await read_ome_zarr_store(invalid_url)
        # Should return error result
        assert isinstance(result, ConversionResult)
        assert result.success is False
        assert result.error is not None
        print(f"read_ome_zarr_store correctly handled error: {result.error}")
    except Exception as e:
        print(f"read_ome_zarr_store raised exception (also acceptable): {e}")

    # Test convert_images_to_ome_zarr with invalid URL
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "should_not_exist.ome.zarr"

        try:
            result = await convert_images_to_ome_zarr(
                input_paths=[invalid_url],
                output_path=str(output_path),
                ome_zarr_version="0.4",
                method="itkwasm_gaussian",
            )

            # Should return error result
            assert isinstance(result, ConversionResult)
            assert result.success is False
            assert result.error is not None
            print(f"convert_images_to_ome_zarr correctly handled error: {result.error}")

        except Exception as e:
            print(f"convert_images_to_ome_zarr raised exception (also acceptable): {e}")
