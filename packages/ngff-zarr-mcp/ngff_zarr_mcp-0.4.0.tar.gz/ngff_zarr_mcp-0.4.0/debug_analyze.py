#!/usr/bin/env python3
"""Debug script to test analyze_zarr_store function."""

import tempfile
from pathlib import Path
import zarr
from ngff_zarr_mcp.tools import convert_to_ome_zarr
from ngff_zarr_mcp.models import ConversionOptions
import asyncio
from rich import print


async def test_analyze_debug():
    # Get the test input file
    test_input_file = Path('test/data/input/MR-head.nrrd')
    test_input_file = 'https://dandiarchive.s3.amazonaws.com/zarr/ca578830-fb23-4aa6-8471-cfde8478abfb'
    # if not test_input_file.exists():
    #     print('Test input file not found, skipping')
    #     return

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / 'test_v05.ome.zarr'
        output_path = 'test_v05.ome.zarr'

        options = ConversionOptions(
            output_path=str(output_path),
            ome_zarr_version='0.5',
            method='itkwasm_gaussian',
            chunks=64,
        )

        result = await convert_to_ome_zarr([str(test_input_file)], options)

        print(f"Conversion result: {result}")

        # if result.success:
        #     store_path = str(output_path)

        #     # Reproduce the analyze_zarr_store logic step by step
        #     try:
        #         from ngff_zarr import from_ngff_zarr

        #         print("Loading multiscales...")
        #         multiscales = from_ngff_zarr(store_path)
        #         first_image = multiscales.images[0]
        #         print(f"Loaded {len(multiscales.images)} scales")

        #         print("Opening zarr store...")
        #         root = zarr.open(store_path, mode="r")
        #         print(f"Root attrs keys: {list(root.attrs.keys())}")

        #         # Determine OME-Zarr version from metadata
        #         version = "0.4"  # Default
        #         print("Checking version...")

        #         # Check for v0.5 format first (ome.version)
        #         if "ome" in root.attrs:
        #             print("Found 'ome' in root.attrs")
        #             ome_attrs = root.attrs["ome"]
        #             print(f"ome_attrs type: {type(ome_attrs)}")
        #             print(f"ome_attrs: {ome_attrs}")

        #             if isinstance(ome_attrs, dict):
        #                 print("ome_attrs is dict")
        #                 if "version" in ome_attrs:
        #                     print("Found 'version' in ome_attrs")
        #                     version_attr = ome_attrs["version"]
        #                     print(f"version_attr: {version_attr}, type: {type(version_attr)}")
        #                     if isinstance(version_attr, str):
        #                         print("version_attr is string")
        #                         version = version_attr
        #                         print(f"Set version to: {version}")
        #                     else:
        #                         print("version_attr is not string")
        #                 else:
        #                     print("'version' not in ome_attrs")
        #             else:
        #                 print("ome_attrs is not dict")
        #         else:
        #             print("'ome' not in root.attrs")
        #             # Check for v0.4 format (multiscales[0].version)
        #             if "multiscales" in root.attrs:
        #                 print("Found 'multiscales' in root.attrs")
        #                 multiscales_attr = root.attrs["multiscales"]
        #                 if isinstance(multiscales_attr, list) and len(multiscales_attr) > 0:
        #                     ms_attrs = multiscales_attr[0]
        #                     if isinstance(ms_attrs, dict) and "version" in ms_attrs:
        #                         version_attr = ms_attrs["version"]
        #                         if isinstance(version_attr, str):
        #                             version = version_attr
        #                             print(f"Set version from multiscales to: {version}")
        #             else:
        #                 print("'multiscales' not in root.attrs")

        #         print(f"Final version: {version}")

        #     except Exception as e:
        #         print(f"Exception in version detection: {e}")
        #         import traceback
        #         traceback.print_exc()

        # else:
        #     print('Conversion failed:', result.error)


if __name__ == "__main__":
    asyncio.run(test_analyze_debug())
