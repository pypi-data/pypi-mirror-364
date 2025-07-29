"""File watching and remote polling functionality."""

import time
import requests
from pathlib import Path
from threading import Timer, Thread, Event
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .file_processors import process_source_file, delete_source_views


class DebouncedChangeHandler(FileSystemEventHandler):
    """A debounced handler that processes a batch of file changes after a quiet period."""

    def __init__(self, config, db_connection):
        self.debounce_timer = None
        self.changed_files = set()
        self.deleted_files = set()
        self.config = config
        self.db_connection = db_connection
        self.debounce_seconds = config.get('debounce_seconds', 2.0)

    def dispatch_event(self, event):
        if event.is_directory:
            return

        path = event.src_path
        if event.event_type == 'deleted':
            self.deleted_files.add(path)
            if path in self.changed_files:
                self.changed_files.remove(path)
        else:  # created, modified
            self.changed_files.add(path)
            if path in self.deleted_files:
                self.deleted_files.remove(path)

        if self.debounce_timer:
            self.debounce_timer.cancel()
        self.debounce_timer = Timer(self.debounce_seconds, self.process_changes)
        self.debounce_timer.start()

    def on_any_event(self, event):
        self.dispatch_event(event)

    def process_changes(self):
        print(f"\n--- Debounced Event: Processing {len(self.changed_files) + len(self.deleted_files)} changes ---")
        # Process deletions first
        for f in self.deleted_files:
            delete_source_views(f, self.db_connection, self.config)
        # Then process creations/modifications
        for f in self.changed_files:
            # A modification is like a delete then a create
            delete_source_views(f, self.db_connection, self.config)
            process_source_file(f, self.db_connection, self.config)

        self.changed_files.clear()
        self.deleted_files.clear()
        print("--- Finished processing batch. Waiting for next change... ---")


class FileWatcher:
    """Manages file system watching and remote polling."""

    def __init__(self, config, db_connection):
        self.config = config
        self.db_connection = db_connection
        self.observer = None
        self.poller_thread = None
        self.poller_stop_event = Event()

    def start(self):
        """Starts file watching and remote polling."""
        print("✅ Starting file watcher... (Press Ctrl+C to exit)")
        print("Watcher will update the DuckDB catalog in real-time.")

        event_handler = DebouncedChangeHandler(self.config, self.db_connection)
        self.observer = Observer()

        # Separate sources by type
        remote_uris = []
        for source in self.config['sources']:
            if source.startswith(('http://', 'https://', 's3://')):
                remote_uris.append(source)

        # Set up local file watching
        watch_paths = {str(Path(s.split('**')[0].split('*')[0])) for s in self.config['sources'] if
                       not s.startswith(('http', 'sqlite', 's3'))}

        for path in watch_paths:
            if Path(path).is_dir():
                self.observer.schedule(event_handler, path, recursive=True)
                print(f"  -> Watching directory: {path}")
            elif Path(path).exists():
                # Watch the parent directory if it's a single file
                parent_dir = str(Path(path).parent)
                self.observer.schedule(event_handler, parent_dir, recursive=False)
                print(f"  -> Watching parent directory for file: {path}")

        self.observer.start()

        # Start the remote poller if enabled
        if self.config.get('polling_interval_seconds', 0) > 0:
            self.poller_thread = Thread(
                target=self._poll_remote_sources,
                args=(remote_uris,),
                daemon=True
            )
            self.poller_thread.start()

    def stop(self):
        """Stops file watching and remote polling."""
        if self.observer:
            self.observer.stop()
            self.observer.join()

        if self.poller_thread:
            self.poller_stop_event.set()
            self.poller_thread.join()

        print("\nWatcher stopped.")

    def wait(self):
        """Waits for the watcher to be interrupted."""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def _poll_remote_sources(self, remote_uris):
        """Periodically checks remote sources for changes."""
        if not remote_uris:
            return

        polling_interval = self.config.get('polling_interval_seconds', 0)
        if polling_interval <= 0:
            print("-> Remote polling is disabled (polling_interval_seconds is 0 or not set).")
            return

        print(f"-> Starting remote poller for {len(remote_uris)} URIs (interval: {polling_interval}s)")
        last_seen_etags = {}

        while not self.poller_stop_event.is_set():
            for uri in remote_uris:
                try:
                    current_etag = None
                    if uri.startswith('s3://'):
                        # S3 ETag checking requires s3fs
                        import s3fs
                        fs = s3fs.S3FileSystem()
                        current_etag = fs.info(uri).get('ETag')
                    else:  # HTTP/S
                        response = requests.head(uri, allow_redirects=True, timeout=10)
                        response.raise_for_status()
                        current_etag = response.headers.get('ETag') or response.headers.get('Last-Modified')

                    if current_etag and last_seen_etags.get(uri) != current_etag:
                        print(f"\n[REMOTE CHANGE DETECTED] {uri}")
                        # Re-processing is like a delete then create
                        delete_source_views(uri, self.db_connection, self.config)
                        process_source_file(uri, self.db_connection, self.config)
                        last_seen_etags[uri] = current_etag
                    elif not current_etag:
                        print(
                            f"  -> Warning: Could not get ETag/Last-Modified for {uri}. Will not be able to detect changes.")
                        # Process once if never seen before
                        if uri not in last_seen_etags:
                            process_source_file(uri, self.db_connection, self.config)
                            last_seen_etags[uri] = 'processed_once'

                except Exception as e:
                    print(f"  -> Warning: Could not poll remote source {uri}. Error: {e}")

            self.poller_stop_event.wait(polling_interval)
