"""Utility functions for duck-tape."""

import re
import duckdb
from pathlib import Path
from urllib.parse import urlparse


def sanitize_name(name):
    """Sanitizes a string to be a valid SQL identifier."""
    if not isinstance(name, str):
        name = str(name)
    name = re.sub(r'[\\/\s.-]', '_', name)
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    name = name.lower()
    return name.strip('_')


def generate_table_name(source, optional_part=None):
    """Creates a descriptive and unique table name from a file path or URL."""
    source_str = str(source)
    if source_str.startswith(('http://', 'https://', 's3://', 'sqlite://')):
        parsed_url = urlparse(source_str)
        path_parts = parsed_url.path.strip('/').split('/')
        stem = Path(path_parts[-1]).stem if path_parts[-1] else "index"
        parts = [parsed_url.netloc] + path_parts[:-1] + [stem]
    else:
        p = Path(source)
        parts = list(p.parts[:-1]) + [p.stem]
    if optional_part:
        parts.append(str(optional_part))
    return '_'.join(sanitize_name(part) for part in parts if part)


def get_db_connection(config):
    """Creates and configures a DuckDB connection."""
    db = duckdb.connect(database=config['output_db_file'], read_only=False)
    db.execute("INSTALL httpfs; LOAD httpfs;")
    if config.get('s3', {}).get('region'):
        db.execute(f"SET s3_region='{config['s3']['region']}';")
    if config.get('s3', {}).get('endpoint'):
        db.execute(f"SET s3_endpoint='{config['s3']['endpoint']}';")
    if config.get('s3', {}).get('url_style'):
        db.execute(f"SET s3_url_style='{config['s3']['url_style']}';")
    return db
