#!/usr/bin/env python3
"""Test script to test tensorstore compression directly from MCP environment."""

import tempfile
from pathlib import Path
import sys

# Add the py directory to the path so we can import the modified ngff_zarr
sys.path.insert(0, '../py')

from ngff_zarr import to_ngff_zarr, cli_input_to_ngff_image, detect_cli_io_backend, to_multiscales
import numcodecs


def test_tensorstore_compression():
    test_input_file = Path('test/data/input/MR-head.nrrd')
    if test_input_file.exists():
        print('Found test file')
        backend = detect_cli_io_backend([str(test_input_file)])
        print('Detected backend:', backend)
        ngff_image = cli_input_to_ngff_image(backend, [str(test_input_file)])
        print('Loaded image')
        
        multiscales = to_multiscales(ngff_image)
        print('Created multiscales')
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = f'{temp_dir}/test.ome.zarr'
            print('Testing compression with tensorstore...')
            
            try:
                compressor = numcodecs.Blosc(cname='lz4', clevel=5)
                print('Created compressor:', compressor)
                to_ngff_zarr(
                    output_path,
                    multiscales,
                    version='0.4',
                    use_tensorstore=True,
                    compressor=compressor
                )
                print('Success!')
            except Exception as e:
                print(f'Error: {e}')
                import traceback
                traceback.print_exc()
    else:
        print('Test file not found')


if __name__ == "__main__":
    test_tensorstore_compression()
