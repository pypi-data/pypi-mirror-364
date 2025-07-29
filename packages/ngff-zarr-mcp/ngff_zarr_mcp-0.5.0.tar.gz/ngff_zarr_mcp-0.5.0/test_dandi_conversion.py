#!/usr/bin/env python3
"""
Test script for convert_images_to_ome_zarr with DANDI zarr store.
"""

import asyncio
import sys
import os

# Add the MCP package to path
sys.path.insert(0, "/home/matt/src/ngff-zarr/mcp")

from ngff_zarr_mcp.tools import convert_to_ome_zarr
from ngff_zarr_mcp.models import ConversionOptions


async def test_dandi_conversion():
    """Test converting DANDI zarr store to OME-Zarr."""

    print("Testing convert_images_to_ome_zarr with DANDI zarr store...\n")

    # Test parameters matching the user's request
    input_paths = [
        "https://dandiarchive.s3.amazonaws.com/zarr/ca578830-fb23-4aa6-8471-cfde8478abfb"
    ]

    options = ConversionOptions(
        output_path="dandi-set-108.ome.zarr",
        ome_zarr_version="0.5",
        chunks=[1, 1, 128, 128, 128],  # t, c, z, y, x
        chunks_per_shard=[1, 1, 128, 128, 128],  # t, c, z, y, x
        use_tensorstore=False,  # Disable tensorstore for testing
    )

    try:
        print(f"Input: {input_paths[0]}")
        print(f"Output: {options.output_path}")
        print(f"OME-Zarr version: {options.ome_zarr_version}")
        print(f"Chunks: {options.chunks}")
        print(f"Chunks per shard: {options.chunks_per_shard}")
        print(f"Use tensorstore: {options.use_tensorstore}")
        print()

        result = await convert_to_ome_zarr(input_paths, options)

        if result.success:
            print("✅ Conversion successful!")
            print(f"Output path: {result.output_path}")

            if result.store_info:
                print("Store info:")
                for key, value in result.store_info.items():
                    print(f"  {key}: {value}")
        else:
            print("❌ Conversion failed!")
            print(f"Error: {result.error}")

    except Exception as e:
        print(f"❌ Exception during conversion: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_dandi_conversion())
