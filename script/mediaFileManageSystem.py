import json
import logging

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Configuration
CONFIG_FILE = 'config.json'
LOG_FILE = 'file_management.log'

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load configuration from a JSON file
with open(CONFIG_FILE, 'r') as config_file:
    config = json.load(config_file)


class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        # This function is called when a file is created
        if event.is_directory:
            return
        try:
            self.process(event.src_path)
        except Exception as e:
            logging.error(f"Failed to process {event.src_path}: {e}")

    def process(self, file_path):
        logging.info(f"Processing file: {file_path}")
        # Extract metadata
        metadata = self.extract_metadata(file_path)

        # Organize file
        self.organize_file(file_path, metadata)

    def extract_metadata(self, file_path):
        # TODO: Extract metadata from the file or accompanying JSON
        return {}

    def organize_file(self, file_path, metadata):
        # TODO: Rename and move file according to the extracted metadata and configuration
        pass


def main():
    path = config['watch_directory']
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    logging.info(f"Monitoring directory: {path}")
    try:
        while True:
            # Run indefinitely
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
