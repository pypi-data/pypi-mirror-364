#!/usr/bin/env python3
"""Test script to verify memory_target removal."""

from ngff_zarr_mcp.models import ConversionOptions

# Test creating ConversionOptions without memory_target
options = ConversionOptions(
    output_path="test.ome.zarr",
    ome_zarr_version="0.4"
)

print(f"ConversionOptions created successfully:")
print(f"  output_path: {options.output_path}")
print(f"  ome_zarr_version: {options.ome_zarr_version}")
print(f"  use_local_cluster: {options.use_local_cluster}")
print(f"  cache_dir: {options.cache_dir}")

# Verify memory_target is not in the model
if hasattr(options, 'memory_target'):
    print("ERROR: memory_target still exists in ConversionOptions")
else:
    print("SUCCESS: memory_target has been removed from ConversionOptions")

print("Test completed successfully!")
