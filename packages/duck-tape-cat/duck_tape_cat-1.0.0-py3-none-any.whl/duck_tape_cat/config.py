"""Configuration management for duck-tape."""

import os
import yaml

DEFAULT_CONFIG = {
    'sources': ['data/**/*'],
    'output_db_file': 'data_catalog.duckdb',
    'intermediate_dir': 'intermediate_data',
    'debounce_seconds': 2.0,
    'polling_interval_seconds': 60,  # Set to 0 to disable remote polling
    'convert_to_parquet_min_mb': 50,
    'convert_to_parquet_max_mb': 1024,
    's3': {
        'region': None,
        'endpoint': None,
        'url_style': 'vhost'
    },
    'excel_table_discovery': {
        'min_rows': 3,
        'min_cols': 2,
        'max_header_rows': 5  # Max rows to look for titles/grouped headers
    },
    'xml_table_discovery': {
        'min_records': 3,
        'max_depth': 5
    }
}

SUPPORTED_EXTENSIONS = [
    '.csv', '.json', '.xlsx', '.xls', '.xml', '.yaml', '.yml',
    '.html', '.htm', '.md', '.parquet', '.arrow', '.feather',
    '.avro', '.orc'
]

# Check for PDF support
PDF_SUPPORT_ENABLED = False
try:
    import camelot
    import shutil
    if shutil.which("ghostscript"):
        PDF_SUPPORT_ENABLED = True
        SUPPORTED_EXTENSIONS.append('.pdf')
    else:
        print(
            "Warning: The 'camelot-py' library is installed, but Ghostscript is not found in your system's PATH. "
            "PDF processing will be disabled. Please install Ghostscript to enable PDF support.")
except ImportError:
    print(
        "Warning: 'camelot-py' is not installed. PDF processing will be disabled. "
        "To enable, run: pip install 'camelot-py[cv]'")


def load_config(config_path):
    """Loads configuration from YAML file and overrides with environment variables."""
    config = DEFAULT_CONFIG.copy()

    if os.path.exists(config_path):
        print(f"-> Loading configuration from '{config_path}'")
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                # Deep merge dictionaries
                for key, value in yaml_config.items():
                    if isinstance(value, dict) and isinstance(config.get(key), dict):
                        config[key].update(value)
                    else:
                        config[key] = value
    else:
        print(f"-> Config file '{config_path}' not found. Using defaults and environment variables.")

    env_overrides = {
        'sources': os.getenv('DUCKTAPE_SOURCES'),
        'output_db_file': os.getenv('DUCKTAPE_OUTPUT_DB_FILE'),
        'intermediate_dir': os.getenv('DUCKTAPE_INTERMEDIATE_DIR'),
        's3_region': os.getenv('DUCKTAPE_S3_REGION'),
        'polling_interval_seconds': os.getenv('DUCKTAPE_POLLING_INTERVAL_SECONDS'),
    }

    if env_overrides['sources']:
        config['sources'] = [s.strip() for s in env_overrides['sources'].split(',')]
    if env_overrides['output_db_file']:
        config['output_db_file'] = env_overrides['output_db_file']
    if env_overrides['intermediate_dir']:
        config['intermediate_dir'] = env_overrides['intermediate_dir']
    if env_overrides['s3_region']:
        config['s3']['region'] = env_overrides['s3_region']
    if env_overrides['polling_interval_seconds']:
        try:
            config['polling_interval_seconds'] = int(env_overrides['polling_interval_seconds'])
        except (ValueError, TypeError):
            pass  # Keep default if env var is invalid

    return config
