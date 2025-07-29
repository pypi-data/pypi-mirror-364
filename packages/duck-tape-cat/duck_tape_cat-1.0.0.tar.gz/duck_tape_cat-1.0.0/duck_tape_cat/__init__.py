"""
duck-tape: Build DuckDB data catalogs from various sources.
"""

from .catalog_builder import CatalogBuilder
from .file_watcher import FileWatcher
from .config import load_config

__all__ = ['CatalogBuilder', 'FileWatcher', 'load_config']

__version__ = "1.0.0"
__author__ = "Kenneth Stott"
__email__ = "ken@hasura.io"
__description__="Duck Tape"
