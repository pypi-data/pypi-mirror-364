#!/usr/bin/env python3
"""Debug script to test v0.5 version detection."""

import tempfile
from pathlib import Path
import zarr
from ngff_zarr_mcp.tools import convert_to_ome_zarr
from ngff_zarr_mcp.models import ConversionOptions
from ngff_zarr_mcp.utils import analyze_zarr_store
import asyncio


async def test_version_detection():
    # Get the test input file
    test_input_file = Path('test/data/input/MR-head.nrrd')
    if not test_input_file.exists():
        print('Test input file not found, skipping')
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / 'test_v05.ome.zarr'
        
        options = ConversionOptions(
            output_path=str(output_path),
            ome_zarr_version='0.5',
            method='itkwasm_gaussian',
            chunks=64,
        )
        
        result = await convert_to_ome_zarr([str(test_input_file)], options)
        
        if result.success:
            # Check what's actually in the zarr store
            root = zarr.open(str(output_path), mode='r')
            print('Root attributes keys:', list(root.attrs.keys()))
            
            if 'ome' in root.attrs:
                ome_attrs = root.attrs['ome']
                print('ome attrs:', ome_attrs)
                print('ome attrs type:', type(ome_attrs))
                if isinstance(ome_attrs, dict):
                    print('ome attrs keys:', list(ome_attrs.keys()))
                    if 'version' in ome_attrs:
                        version_attr = ome_attrs['version']
                        print('version attr:', version_attr)
                        print('version attr type:', type(version_attr))
            
            # Now test our analyze function
            store_info = analyze_zarr_store(str(output_path))
            print('Detected version:', store_info.version)
        else:
            print('Conversion failed:', result.error)


if __name__ == "__main__":
    asyncio.run(test_version_detection())
