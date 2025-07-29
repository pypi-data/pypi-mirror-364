#!/usr/bin/env python3
"""Debug script to test remote OME-Zarr store access."""

import asyncio
from ngff_zarr_mcp.server import get_ome_zarr_info

REMOTE_STORE_URL = (
    "https://dandiarchive.s3.amazonaws.com/zarr/ca578830-fb23-4aa6-8471-cfde8478abfb/"
)


async def main():
    try:
        print(f"Testing remote store: {REMOTE_STORE_URL}")
        result = await get_ome_zarr_info(REMOTE_STORE_URL)
        print("Success!")
        print(f"Store info: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
