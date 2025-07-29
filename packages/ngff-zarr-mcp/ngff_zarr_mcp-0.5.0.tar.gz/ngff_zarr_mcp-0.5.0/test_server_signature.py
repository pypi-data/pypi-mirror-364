#!/usr/bin/env python3
"""Test script to verify server function signature."""

import inspect
from ngff_zarr_mcp.server import convert_images_to_ome_zarr

# Get the function signature
sig = inspect.signature(convert_images_to_ome_zarr)

print("convert_images_to_ome_zarr function parameters:")
for name, param in sig.parameters.items():
    print(f"  {name}: {param.annotation} = {param.default}")

# Check if memory_target is in parameters
if 'memory_target' in sig.parameters:
    print("ERROR: memory_target still exists in function signature")
else:
    print("SUCCESS: memory_target has been removed from function signature")

print("Test completed successfully!")
