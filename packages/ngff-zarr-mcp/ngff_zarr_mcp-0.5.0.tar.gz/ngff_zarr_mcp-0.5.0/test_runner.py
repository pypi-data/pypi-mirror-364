#!/usr/bin/env python3
"""Simple test runner for convert_to_ome_zarr functionality."""

import asyncio
import tempfile
from pathlib import Path

from ngff_zarr_mcp.tools import convert_to_ome_zarr
from ngff_zarr_mcp.models import ConversionOptions


async def test_conversion():
    """Test the basic conversion functionality."""
    # Path to test input file
    test_input_file = Path(__file__).parent / "test" / "data" / "input" / "MR-head.nrrd"

    if not test_input_file.exists():
        print(f"❌ Test input file not found: {test_input_file}")
        return False

    print(f"✅ Found test input file: {test_input_file}")

    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "mr_head_test.ome.zarr"

        # Configure conversion options
        options = ConversionOptions(
            output_path=str(output_path),
            ome_zarr_version="0.4",
            chunks=64,
        )

        print(f"🔄 Converting {test_input_file.name} to OME-Zarr...")

        # Perform conversion
        result = await convert_to_ome_zarr([str(test_input_file)], options)

        if result.success:
            print("✅ Conversion successful!")
            print(f"   Output: {result.output_path}")
            print(f"   Store info: {result.store_info}")
            return True
        else:
            print(f"❌ Conversion failed: {result.error}")
            return False


if __name__ == "__main__":
    success = asyncio.run(test_conversion())
    exit(0 if success else 1)
