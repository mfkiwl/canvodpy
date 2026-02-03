#!/usr/bin/env python3
"""Check actual GFZ product names on ESA FTP server."""

import re
import urllib.request


def check_esa_ftp_files():
    """Check what GFZ files are actually named on ESA server."""

    # GPS week 2279 (September 2023)
    url = "ftp://gssc.esa.int/gnss/products/2279/"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            listing = response.read().decode("utf-8")

            # Find all GFZ/GBM related files
            lines = listing.strip().split("\n")
            gfz_files = []

            for line in lines:
                # Look for GFZ or GBM in the line
                if "GFZ" in line or "GBM" in line or "GF" in line or "GB" in line:
                    gfz_files.append(line)

            print("=" * 80)
            print("GFZ-related files on ESA FTP (GPS week 2279):")
            print("=" * 80)

            if gfz_files:
                for f in sorted(set(gfz_files))[:30]:
                    print(f)
            else:
                print("No GFZ files found")

            # Try to extract just filenames
            print("\n" + "=" * 80)
            print("Extracted filenames:")
            print("=" * 80)

            filenames = []
            for line in lines:
                # Match patterns like GFZ0... or GBM0...
                match = re.search(
                    r"(G[BF][MZ]0[A-Z]+_\d+_\d+_\d+_[A-Z]+\.(SP3|CLK))",
                    line,
                    re.IGNORECASE,
                )
                if match:
                    filenames.append(match.group(1))

            for fn in sorted(set(filenames)):
                print(fn)

    except Exception as e:
        print(f"Error accessing ESA FTP: {e}")
        print("\nThis might be due to network issues.")
        print("Try manually checking: ftp://gssc.esa.int/gnss/products/2279/")


if __name__ == "__main__":
    check_esa_ftp_files()
