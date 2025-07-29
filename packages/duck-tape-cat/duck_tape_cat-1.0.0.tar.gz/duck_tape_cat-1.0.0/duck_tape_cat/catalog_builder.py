"""Main catalog building functionality."""

import os
import glob
import shutil
from pathlib import Path
from .utils import get_db_connection, generate_table_name
from .file_processors import process_source_file
from .file_watcher import FileWatcher


class CatalogBuilder:
    """Manages the building and maintenance of DuckDB data catalogs."""

    def __init__(self, config):
        self.config = config
        self.db_connection = None

    def build(self):
        """Performs a full, clean build of the DuckDB catalog."""
        print("--- Starting Full Catalog Build ---")

        # Ensure local intermediate directory exists
        if not self.config['intermediate_dir'].startswith('s3://'):
            # Clean and create the intermediate directory
            if os.path.exists(self.config['intermediate_dir']):
                shutil.rmtree(self.config['intermediate_dir'])
                print(f"Removed existing intermediate directory: {self.config['intermediate_dir']}")
            os.makedirs(self.config['intermediate_dir'])
            print(f"Created clean intermediate directory: {self.config['intermediate_dir']}")

        # Ensure output directory exists and remove old DB file
        output_db_path = Path(self.config['output_db_file'])
        output_db_path.parent.mkdir(parents=True, exist_ok=True)
        if output_db_path.exists():
            os.remove(output_db_path)
            print(f"Removed existing database file: {output_db_path}")

        self.db_connection = get_db_connection(self.config)

        # Separate sources by type
        local_globs, remote_uris, db_uris = self._categorize_sources()

        # Process local files
        local_files = []
        for pattern in local_globs:
            local_files.extend(glob.glob(pattern, recursive=True))

        all_file_sources = [f for f in local_files if not Path(f).is_dir()] + remote_uris

        print(f"Found {len(all_file_sources)} files/URIs and {len(db_uris)} database connections to process.")

        # Process all file sources
        for source_path in all_file_sources:
            process_source_file(source_path, self.db_connection, self.config)

        # Process database sources
        for db_uri in db_uris:
            self._process_database_source(db_uri)

        self.db_connection.close()
        print(f"\n✅ Catalog build complete. File is at: {self.config['output_db_file']}")

    def watch(self):
        """Starts watching for changes and updating the catalog in real-time."""
        print("\nPerforming initial build before starting watcher...")
        self.build()

        # Reopen connection for watching
        self.db_connection = get_db_connection(self.config)

        watcher = FileWatcher(self.config, self.db_connection)
        watcher.start()
        watcher.wait()
        watcher.stop()

        self.db_connection.close()

    def _categorize_sources(self):
        """Separates sources into local globs, remote URIs, and database URIs."""
        local_globs, remote_uris, db_uris = [], [], []

        for source in self.config['sources']:
            if source.startswith('sqlite://'):
                db_uris.append(source)
            elif source.startswith(('http://', 'https://', 's3://')):
                remote_uris.append(source)
            else:
                local_globs.append(source)

        return local_globs, remote_uris, db_uris

    def _process_database_source(self, db_uri):
        """Processes database sources (e.g., SQLite)."""
        try:
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                print(f"  -> Creating VIEWs for SQLite DB: {db_path}")
                self.db_connection.execute("INSTALL sqlite; LOAD sqlite;")
                escaped_db_path = db_path.replace("'", "''")
                tables = self.db_connection.execute(
                    f"SELECT name FROM sqlite_scan('{escaped_db_path}', 'sqlite_master') WHERE type='table';").fetchall()
                for (table_name, ) in tables:
                    view_name = generate_table_name(db_path, table_name)
                    print(f"    -> Creating VIEW '{view_name}' for table '{table_name}'")
                    escaped_table_name = table_name.replace("'", "''")
                    self.db_connection.execute(
                        f"""CREATE OR REPLACE VIEW "{view_name}" AS SELECT * FROM sqlite_scan('{escaped_db_path}', '{escaped_table_name}');""")
        except Exception as e:
            print(f"  ❌ Error processing database {db_uri}: {e}")
