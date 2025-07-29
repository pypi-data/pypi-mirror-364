#!/usr/bin/env python3
"""Debug script to inspect OME-Zarr metadata."""

import asyncio
import tempfile
import zarr
from pathlib import Path

from ngff_zarr_mcp.tools import convert_to_ome_zarr
from ngff_zarr_mcp.models import ConversionOptions


async def debug_version():
    """Debug the version issue."""
    # Path to test input file
    test_input_file = Path(__file__).parent / "test" / "data" / "input" / "MR-head.nrrd"

    if not test_input_file.exists():
        print(f"❌ Test input file not found: {test_input_file}")
        return False

    print(f"✅ Found test input file: {test_input_file}")

    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "mr_head_v05_debug.ome.zarr"

        # Configure conversion options for v0.5
        options = ConversionOptions(
            output_path=str(output_path),
            ome_zarr_version="0.5",
            method="itkwasm_gaussian",
            chunks=64,
        )

        print(f"🔄 Converting {test_input_file.name} to OME-Zarr v0.5...")

        # Perform conversion
        result = await convert_to_ome_zarr([str(test_input_file)], options)

        if result.success:
            print("✅ Conversion successful!")
            print(f"   Output: {result.output_path}")

            # Now let's inspect the metadata manually
            root = zarr.open(str(output_path), mode="r")

            print(f"📋 Root attributes: {dict(root.attrs)}")

            if "multiscales" in root.attrs:
                multiscales_attr = root.attrs["multiscales"]
                print(f"🔍 Multiscales attribute: {multiscales_attr}")

                if isinstance(multiscales_attr, list) and len(multiscales_attr) > 0:
                    ms_attrs = multiscales_attr[0]
                    print(f"🔍 First multiscales item: {ms_attrs}")

                    if isinstance(ms_attrs, dict) and "version" in ms_attrs:
                        version_attr = ms_attrs["version"]
                        print(
                            f"🎯 Version found: {version_attr} (type: {type(version_attr)})"
                        )
                    else:
                        print("❌ No version found in multiscales metadata")
                        print(
                            f"   Available keys: {list(ms_attrs.keys()) if isinstance(ms_attrs, dict) else 'Not a dict'}"
                        )
            else:
                print("❌ No multiscales attribute found")

            return True
        else:
            print(f"❌ Conversion failed: {result.error}")
            return False


if __name__ == "__main__":
    success = asyncio.run(debug_version())
    exit(0 if success else 1)
