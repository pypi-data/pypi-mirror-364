#!/usr/bin/env python3
"""Simple test script for convert_to_ome_zarr function."""

import asyncio
import tempfile
import shutil
from pathlib import Path

from ngff_zarr_mcp.tools import convert_to_ome_zarr
from ngff_zarr_mcp.models import ConversionOptions


async def main():
    # Path to test input file
    test_input_file = Path("test/data/input/MR-head.nrrd")

    if not test_input_file.exists():
        print(f"Test input file not found: {test_input_file}")
        return

    # Create temp output directory
    temp_dir = tempfile.mkdtemp()
    output_path = Path(temp_dir) / "mr_head.ome.zarr"

    try:
        # Configure conversion options
        options = ConversionOptions(
            output_path=str(output_path),
            ome_zarr_version="0.4",
            method="itkwasm_gaussian",
            # Single scale (no multiscale)
            scale_factors=None,
            # Use small chunks for testing
            chunks=64,
        )

        print(f"Converting {test_input_file} to {output_path}")

        # Perform conversion
        result = await convert_to_ome_zarr([str(test_input_file)], options)

        if result.success:
            print("✓ Conversion succeeded!")
            print(f"Output: {result.output_path}")
            print(f"Store info: {result.store_info}")
        else:
            print(f"✗ Conversion failed: {result.error}")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
