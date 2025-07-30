#!/usr/bin/env python3
"""
Command-line interface for IronShield.
"""

import argparse
import sys
from . import ironshield, __version__

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="IronShield - A comprehensive security toolkit for Python applications"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"IronShield {__version__}"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize IronShield"
    )
    parser.add_argument(
        "--info",
        action="store_true", 
        help="Show package information"
    )

    args = parser.parse_args()

    if args.init:
        ironshield.init()
    elif args.info:
        info = ironshield.info()
        print(f"Name: {info['name']}")
        print(f"Version: {info['version']}")
        print(f"Description: {info['description']}")
    else:
        parser.print_help()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main()) 