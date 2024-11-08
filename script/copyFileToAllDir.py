import os
import shutil


def copy_file_to_all_subdirs(file_path, target_dir):
    '''
    Copies a file to all subdirectories within the target directory.

    Parameters:
    - file_path: Path to the file to be copied.
    - target_dir: Directory under which all subdirectories will receive a copy of the file.
    '''
    for root, dirs, files in os.walk(target_dir):
        for dir in dirs:
            shutil.copy(file_path, os.path.join(root, dir))
            print(f'Copied {file_path} to {os.path.join(root, dir)}')


if __name__ == '__main__':
    copy_file_to_all_subdirs('/Users/flamenco/Library/CloudStorage/OneDrive-个人/媒体库/XXX/Pornhub/.nomedia','/Users/flamenco/Library/CloudStorage/OneDrive-个人/媒体库/ASMR/橙子汉化');