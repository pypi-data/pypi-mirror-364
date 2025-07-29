#!/usr/bin/env python3
"""Test script to reproduce the tensorstore compression issue."""

import tempfile
from pathlib import Path
import sys

# Force using the local development version of ngff-zarr
sys.path.insert(0, '../py')

from ngff_zarr_mcp.tools import convert_to_ome_zarr
from ngff_zarr_mcp.models import ConversionOptions
import asyncio


async def test_tensorstore_compression():
    # Get the test input file
    test_input_file = Path('test/data/input/MR-head.nrrd')
    if not test_input_file.exists():
        print('Test input file not found, skipping')
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / 'test_tensorstore_compression.ome.zarr'
        
        options = ConversionOptions(
            output_path=str(output_path),
            ome_zarr_version='0.4',
            method='itkwasm_gaussian',
            chunks=64,
            compression_codec='blosc',
            use_tensorstore=True,
        )
        
        result = await convert_to_ome_zarr([str(test_input_file)], options)
        
        if result.success:
            print('Success! Tensorstore with compression worked.')
            print(f'Output path: {result.output_path}')
        else:
            print(f'Conversion failed: {result.error}')


if __name__ == "__main__":
    asyncio.run(test_tensorstore_compression())
