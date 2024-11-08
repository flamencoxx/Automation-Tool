import os
from datetime import datetime
import sys

# Flatten the list of extensions
allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                      '.mp4', '.mkv', '.avi', '.mov', '.wmv',
                      '.srt', '.sub', '.ass',
                      '.mp3', '.wav', '.aac', '.flac']


# Function to rename and move problematic files
def process_files(directory, new_folder="Processed_Files"):
    disallowed_chars = '<>:*?"|\\/'
    log = []
    folder_created = False

    for dirpath, dirnames, filenames in os.walk(directory, topdown=True):
        # Skip the new folder if it exists
        dirnames[:] = [d for d in dirnames if d not in {new_folder}]
        new_folder_path = os.path.join(dirpath, new_folder)

        for filename in filenames:
            if os.path.splitext(filename)[1].lower() in allowed_extensions and any(
                    char in disallowed_chars for char in filename):
                # Create the new folder if it doesn't exist and hasn't been created yet
                if not folder_created and not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
                    log.append(f"Created new directory: {new_folder_path}")
                    folder_created = True

                new_filename = ''.join('_' if c in disallowed_chars else c for c in filename)
                old_file_path = os.path.join(dirpath, filename)
                new_file_path = os.path.join(new_folder_path, new_filename)

                os.rename(old_file_path, new_file_path)
                log.append(f"Processed {old_file_path} -> {new_file_path}")

    if not log:
        log.append("No files needed processing.")

    return log


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_files.py <directory> [new_folder_name]")
        sys.exit(1)

    directory = sys.argv[1]
    new_folder = sys.argv[2] if len(sys.argv) > 2 else "Processed_Files"
    logs = process_files(directory, new_folder)

    # Write the logs to a log file
    log_filename = "processing_log.txt"
    log_path = os.path.join(directory, log_filename)
    with open(log_path, "a") as log_file:
        log_file.write(f"\nLog Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write('\n'.join(logs))
