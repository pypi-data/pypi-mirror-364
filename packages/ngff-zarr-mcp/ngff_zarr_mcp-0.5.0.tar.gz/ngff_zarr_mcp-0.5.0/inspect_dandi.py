#!/usr/bin/env python3
"""
Test script to inspect the DANDI zarr store dimensions.
"""

import sys

sys.path.insert(0, "/home/matt/src/ngff-zarr/py")

from ngff_zarr import from_ngff_zarr

print("Inspecting DANDI zarr store dimensions...\n")

dandi_url = (
    "https://dandiarchive.s3.amazonaws.com/zarr/ca578830-fb23-4aa6-8471-cfde8478abfb"
)

try:
    print(f"Loading: {dandi_url}")
    multiscales = from_ngff_zarr(dandi_url)

    print(f"✅ Successfully loaded multiscales with {len(multiscales.images)} scales")

    # Check the first scale
    if len(multiscales.images) > 0:
        first_image = multiscales.images[0]
        print(f"\nFirst scale details:")
        print(f"  Dims: {first_image.dims}")
        print(f"  Shape: {first_image.data.shape}")
        print(f"  Data type: {first_image.data.dtype}")
        print(f"  Scale: {first_image.scale}")
        print(f"  Translation: {first_image.translation}")

        if hasattr(first_image.data, "chunks"):
            print(f"  Current chunks: {first_image.data.chunks}")

    # Check metadata
    print(f"\nMetadata:")
    print(f"  Version: {multiscales.metadata.version}")
    print(f"  Axes: {[axis.name for axis in multiscales.metadata.axes]}")

    if multiscales.metadata.omero:
        print(f"  OMERO channels: {len(multiscales.metadata.omero.channels)}")

except Exception as e:
    print(f"❌ Failed to load: {e}")
    import traceback

    traceback.print_exc()
