#!/usr/bin/env python3
"""Debug script to inspect remote OME-Zarr store structure."""

import asyncio
import fsspec
import json
import requests

REMOTE_STORE_URL = (
    "https://dandiarchive.s3.amazonaws.com/zarr/ca578830-fb23-4aa6-8471-cfde8478abfb/"
)


async def main():
    print(f"Inspecting remote store: {REMOTE_STORE_URL}")

    # Check if the store exists and what files are available
    try:
        store = fsspec.get_mapper(REMOTE_STORE_URL)
        print("Store mapped successfully")

        # List some files in the store
        print("Checking for zarr metadata files...")

        # Try to get .zattrs file
        try:
            zattrs_url = REMOTE_STORE_URL + ".zattrs"
            response = requests.get(zattrs_url)
            if response.status_code == 200:
                print("Found .zattrs file:")
                print(json.dumps(json.loads(response.text), indent=2))
            else:
                print(f".zattrs not found (status: {response.status_code})")
        except Exception as e:
            print(f"Error getting .zattrs: {e}")

        # Try to get .zgroup file
        try:
            zgroup_url = REMOTE_STORE_URL + ".zgroup"
            response = requests.get(zgroup_url)
            if response.status_code == 200:
                print("Found .zgroup file:")
                print(json.dumps(json.loads(response.text), indent=2))
            else:
                print(f".zgroup not found (status: {response.status_code})")
        except Exception as e:
            print(f"Error getting .zgroup: {e}")

        # Check for OME-Zarr specific metadata
        try:
            ome_url = REMOTE_STORE_URL + "OME"
            response = requests.get(ome_url)
            print(f"OME directory status: {response.status_code}")
        except Exception as e:
            print(f"Error checking OME directory: {e}")

    except Exception as e:
        print(f"Error mapping store: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
