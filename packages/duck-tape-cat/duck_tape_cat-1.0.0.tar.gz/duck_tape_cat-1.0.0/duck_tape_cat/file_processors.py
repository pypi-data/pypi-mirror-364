"""File processing functions for various data formats."""

import os
import pandas as pd
import requests
import markdown
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter
from .utils import generate_table_name, sanitize_name
from .config import PDF_SUPPORT_ENABLED

if PDF_SUPPORT_ENABLED:
    import camelot


def find_tables_in_sheet(df, config):
    """
    Finds and extracts one or more distinct data tables from a raw Excel sheet DataFrame.
    This version includes logic to detect titles and multi-level headers.
    """
    tables = []
    min_rows = config['excel_table_discovery']['min_rows']
    min_cols = config['excel_table_discovery']['min_cols']
    max_header_rows = config['excel_table_discovery']['max_header_rows']

    # Create a boolean mask of non-null cells
    mask = df.notna()

    # Keep processing until all non-null cells have been assigned to a table
    while mask.any().any():
        # Find the first row and column of the next potential table block
        first_row_idx = mask.any(axis=1).idxmax()
        first_col_idx = mask.loc[first_row_idx].idxmax()

        # Find the last row of the contiguous block
        last_row_idx = first_row_idx
        for i in range(first_row_idx, len(df)):
            if not mask.loc[i].any():
                break
            last_row_idx = i

        # Find the last column of the contiguous block
        sub_mask = mask.loc[first_row_idx:last_row_idx]
        last_col_idx = first_col_idx
        for j in range(first_col_idx, len(df.columns)):
            # Check if the column has any data within the block's row boundaries
            if not sub_mask.iloc[:, j - first_col_idx].any():
                break
            last_col_idx = j

        # Extract the full potential table block
        table_block = df.iloc[first_row_idx:last_row_idx + 1, first_col_idx:last_col_idx + 1].copy()

        # Mark this area as processed
        mask.iloc[first_row_idx:last_row_idx + 1, first_col_idx:last_col_idx + 1] = False

        # --- Smarter Header and Title Detection ---
        header_rows_to_skip = 0
        table_alias = None
        header_groups = []

        # Scan the first few rows of the block for titles and headers
        for i in range(min(max_header_rows, len(table_block))):
            row = table_block.iloc[i].dropna()
            non_null_count = len(row)

            # Heuristic: A single-column entry is likely a table title/alias.
            if non_null_count == 1 and not table_alias:
                table_alias = sanitize_name(row.iloc[0])
                header_rows_to_skip = i + 1
                continue

            # Heuristic: A row with fewer entries than columns but more than one is a grouping header
            if 1 < non_null_count < table_block.shape[1] * 0.8:
                header_groups.append(row)
                header_rows_to_skip = i + 1
                continue

            # Heuristic: The first mostly-full row is likely the true header.
            if non_null_count >= table_block.shape[1] * 0.8:
                header_rows_to_skip = i + 1

                # --- Multi-level Header Flattening ---
                new_header = table_block.iloc[i].copy()
                if header_groups:
                    # Forward-fill the grouping headers
                    filled_groups = [group.reindex(new_header.index).ffill() for group in header_groups]
                    # Combine group headers with the column headers
                    new_header = [
                        '_'.join([sanitize_name(g[col]) for g in filled_groups] + [sanitize_name(new_header[col])])
                        for col in new_header.index
                    ]
                else:
                    new_header = [sanitize_name(h) for h in new_header]

                # Assign the new header and break from the header search
                table_block.columns = new_header
                break

        # If no header was found after scanning, skip this block
        if header_rows_to_skip == 0:
            continue

        # Slice the data part of the table (after the headers)
        data_df = table_block.iloc[header_rows_to_skip:].copy()
        data_df = data_df.reset_index(drop=True)
        data_df.columns.name = None

        # Final check for table validity
        if data_df.shape[0] >= min_rows and data_df.shape[1] >= min_cols:
            tables.append((data_df, table_alias))

    return tables


def find_tables_in_xml(root, config):
    """
    Recursively finds and extracts tabular data from an XML tree.
    """
    tables = []
    min_records = config['xml_table_discovery']['min_records']
    max_depth = config['xml_table_discovery']['max_depth']

    def recurse(element, depth):
        if depth > max_depth:
            return

        # Heuristic: A table is a node with many children that have the same tag.
        if len(element) >= min_records:
            tags = [child.tag for child in element]
            tag_counts = Counter(tags)
            # Check if there is at least one common tag
            if not tag_counts:
                return

            most_common_tag, count = tag_counts.most_common(1)[0]

            # If the most common tag makes up > 80% of children, it's likely a table
            if count / len(element) > 0.8:
                records = []
                for child in element:
                    if child.tag == most_common_tag:
                        record = {sub.tag: sub.text for sub in child}
                        # Add attributes of the record element itself
                        record.update(child.attrib)
                        records.append(record)

                if records:
                    tables.append((pd.DataFrame(records), element.tag))
                return  # Stop recursing down this branch once we've found a table

        # If no table found at this level, recurse into children
        for child in element:
            recurse(child, depth + 1)

    recurse(root, 0)
    return tables


def process_source_file(source_path, db_connection, config):
    """
    Processes a single source file, deciding whether to create a direct view
    or convert it to an intermediate Parquet file based on type and size.
    """
    is_local = not str(source_path).startswith(('http', 's3'))
    if is_local and (not os.path.exists(source_path) or os.path.isdir(source_path)):
        print(f"  -> Skipping non-existent or directory path: {source_path}")
        return

    extension = Path(urlparse(str(source_path)).path).suffix.lower()
    from .config import SUPPORTED_EXTENSIONS
    if extension not in SUPPORTED_EXTENSIONS:
        print(f"  -> Skipping unsupported file type: {source_path}")
        return

    strategy = 'direct_view'
    if extension not in ['.csv', '.json', '.parquet', '.feather', '.arrow']:
        strategy = 'convert_to_parquet'
    elif extension in ['.csv', '.json']:
        file_size_mb = 0
        try:
            if is_local:
                file_size_mb = os.path.getsize(source_path) / (1024 * 1024)
            else:
                # For remote files, we need to make a HEAD request
                response = requests.head(str(source_path), allow_redirects=True, timeout=10)
                response.raise_for_status()
                file_size_mb = int(response.headers.get('content-length', 0)) / (1024 * 1024)

            min_mb = config.get('convert_to_parquet_min_mb', 50)
            max_mb = config.get('convert_to_parquet_max_mb', 1024)

            if min_mb <= file_size_mb <= max_mb:
                strategy = 'convert_to_parquet'
                print(f"  -> File '{source_path}' is in performance sweet spot. Converting to Parquet.")
            elif file_size_mb > max_mb:
                print(f"  -> File '{source_path}' is very large. Using direct view to avoid high storage cost.")
            else:
                print(f"  -> File '{source_path}' is small. Using direct view for low latency.")
        except requests.exceptions.RequestException as e:
            print(
                f"  -> Could not determine size of remote file '{source_path}'. Defaulting to direct view. Error: {e}")
        except Exception as e:
            print(
                f"  -> An error occurred determining file size for '{source_path}'. Defaulting to direct view. Error: {e}")

    try:
        if strategy == 'direct_view':
            _create_direct_view(source_path, extension, db_connection, is_local)
        elif strategy == 'convert_to_parquet':
            _convert_to_parquet(source_path, extension, db_connection, config, is_local)

    except Exception as e:
        import traceback
        print(f"  ❌ Error processing source {source_path}: {e}")
        traceback.print_exc()


def _create_direct_view(source_path, extension, db_connection, is_local):
    """Creates a direct view for simple file formats."""
    view_name = generate_table_name(source_path)
    print(f"  -> Creating direct VIEW '{view_name}' for: {source_path}")
    reader_function = {
        '.csv': 'read_csv_auto', '.json': 'read_json_auto', '.parquet': 'read_parquet',
        '.arrow': 'read_ipc', '.feather': 'read_ipc'
    }[extension]
    # Use resolved absolute path for local files to avoid ambiguity
    resolved_path = str(Path(source_path).resolve()) if is_local else str(source_path)
    db_connection.execute(
        f"""CREATE OR REPLACE VIEW "{view_name}" AS SELECT * FROM {reader_function}('{resolved_path.replace("'", "''")}');""")


def _convert_to_parquet(source_path, extension, db_connection, config, is_local):
    """Converts complex file formats to Parquet and creates views."""
    dataframes = []  # This will be a list of tuples: (DataFrame, optional_part)

    if extension in ['.csv', '.json']:
        reader_func = {'csv': 'read_csv_auto', 'json': 'read_json_auto'}[extension[1:]]
        escaped_path = str(source_path).replace("'", "''")
        df = db_connection.execute(f"SELECT * FROM {reader_func}('{escaped_path}')").fetchdf()
        dataframes.append((df, None))

    elif extension in ['.xlsx', '.xls']:
        print(f"  -> Discovering tables in Excel file: {source_path}")
        # For remote files, pandas needs the URL directly. For local, the path.
        xls = pd.ExcelFile(source_path)
        for sheet_name in xls.sheet_names:
            raw_df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            discovered_tables = find_tables_in_sheet(raw_df, config)
            for i, (table_df, table_alias) in enumerate(discovered_tables):
                # Use the discovered alias if available, otherwise generate a generic one
                optional_part = table_alias if table_alias else f"{sheet_name}_table{i}"
                dataframes.append((table_df, optional_part))

    elif extension == '.xml':
        print(f"  -> Discovering tables in XML file: {source_path}")
        # ET.parse can handle file paths and file-like objects
        if is_local:
            tree = ET.parse(source_path)
            root = tree.getroot()
        else:
            response = requests.get(str(source_path), timeout=30)
            response.raise_for_status()
            root = ET.fromstring(response.content)

        discovered_tables = find_tables_in_xml(root, config)
        for df, parent_tag in discovered_tables:
            dataframes.append((df, parent_tag))

    elif extension in ['.avro', '.orc']:
        # These libraries typically read from a file path
        if is_local:
            if extension == '.avro':
                df = pd.read_avro(source_path)
            elif extension == '.orc':
                df = pd.read_orc(source_path)
            dataframes.append((df, None))
        else:
            print(f"  -> Skipping remote Avro/ORC file due to library limitations: {source_path}")

    elif extension in ['.html', '.htm', '.md']:
        if is_local:
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if extension == '.md':
                content = markdown.markdown(content, extensions=['tables'])
        else: # remote URL
            response = requests.get(str(source_path), timeout=10)
            response.raise_for_status()
            content = response.text

        all_html_tables = pd.read_html(content)
        for i, df in enumerate(all_html_tables):
            if df.shape[0] >= config['excel_table_discovery']['min_rows'] and df.shape[1] >= config['excel_table_discovery']['min_cols']:
                dataframes.append((df, f"table{i}"))

    elif extension == '.pdf':
        if PDF_SUPPORT_ENABLED:
            # Camelot requires a local file path
            if is_local:
                pdf_tables = camelot.read_pdf(source_path, pages='all', flavor='lattice')
                for i, table in enumerate(pdf_tables):
                    dataframes.append((table.df, f"page{table.page}_table{i}"))
            else:
                print(f"  -> Skipping remote PDF file as it must be downloaded first: {source_path}")
        else:
            print(f"  -> Skipping PDF file because PDF support is not enabled: {source_path}")

    # Process all discovered dataframes from the source file
    for df, optional_part in dataframes:
        if df.empty:
            print(f"    -> Skipping empty or invalid table from source: {source_path} ({optional_part or ''})")
            continue

        view_name = generate_table_name(source_path, optional_part)

        # Handle local vs S3 intermediate paths
        intermediate_path_str = os.path.join(config['intermediate_dir'], f"{view_name}.parquet")
        if config['intermediate_dir'].startswith('s3://'):
            intermediate_path_str = f"{config['intermediate_dir'].rstrip('/')}/{view_name}.parquet"

        print(f"    -> Saving intermediate Parquet file: {intermediate_path_str}")
        df.to_parquet(intermediate_path_str, index=False)

        # Use resolved path for local files, URI for S3
        resolved_intermediate_path = str(Path(intermediate_path_str).resolve()) if not intermediate_path_str.startswith('s3://') else intermediate_path_str
        print(f"    -> Creating VIEW '{view_name}' for intermediate file")
        db_connection.execute(f"""CREATE OR REPLACE VIEW "{view_name}" AS SELECT * FROM read_parquet('{resolved_intermediate_path.replace("'", "''")}');""")


def delete_source_views(source_path, db_connection, config):
    """Deletes all views and intermediate files associated with a source."""
    print(f"  -> Deleting artifacts for: {source_path}")
    base_name = generate_table_name(source_path)

    intermediate_dir = config['intermediate_dir']
    if intermediate_dir.startswith('s3://'):
        print("  -> S3 cleanup not fully implemented. Dropping views only.")
        # In a real scenario, you'd use s3fs to list and delete files here
    else:
        # This glob pattern is broad to catch tables with discovered aliases
        for f in Path(intermediate_dir).glob(f"{base_name}*.parquet"):
            try:
                view_name_from_file = f.stem
                print(f"    -> Dropping VIEW: {view_name_from_file}")
                db_connection.execute(f'DROP VIEW IF EXISTS "{view_name_from_file}";')
                os.remove(f)
                print(f"    -> Deleted intermediate file: {f}")
            except Exception as e:
                print(f"  ❌ Error during cleanup for {f}: {e}")

    # Drop the direct view if it exists
    db_connection.execute(f'DROP VIEW IF EXISTS "{base_name}";')
