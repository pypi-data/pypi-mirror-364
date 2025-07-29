"""Command-line interface for duck-tape."""

import argparse
from .config import load_config
from .catalog_builder import CatalogBuilder


def main():
    """Main entry point for the duck-tape CLI."""
    parser = argparse.ArgumentParser(
        description="duck-tape: Build or watch a DuckDB data catalog from various sources.")
    parser.add_argument('--config', default='config.yaml', help="Path to the YAML configuration file.")
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument('--build', action='store_true', help="Perform a full, one-time build (default action).")
    mode_group.add_argument('--watch', action='store_true', help="Watch source directories and update the catalog.")
    args = parser.parse_args()

    config = load_config(args.config)
    builder = CatalogBuilder(config)

    # If neither --build nor --watch is specified, default to build.
    if args.watch:
        builder.watch()
    else:  # Default to build mode
        builder.build()


if __name__ == '__main__':
    # To run this script, you may need to install libraries:
    # pip install pandas duckdb pyyaml openpyxl lxml html5lib markdown pyarrow fastavro watchdog requests s3fs
    # For optional PDF support: pip install "camelot-py[cv]"
    main()
