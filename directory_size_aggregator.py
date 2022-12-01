import argparse
import subprocess
import os
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument(
    'path', 
    help='Path of directory',
    type=str
)

BASE_COMMAND_LENGTH = len('file -b --mime-type ')
COMMAND_BUFFER_SIZE = 4096

def main():
    args = parser.parse_args()
    directory_path = args.path

    mimetype_size_map = defaultdict(int)
    file_paths = []
    for root, _, files in os.walk(directory_path):
        for filename in files:
            file_paths.append(root + '/' + filename)

    def execute_file_command(paths):
        raw_result = subprocess.check_output(['file', '-b', '--mime-type', *paths])
        raw_result = raw_result.decode().strip()
        return [_type for _type in raw_result.split('\n') if len(_type.split('/')) == 2]

    
    buffer_count = BASE_COMMAND_LENGTH
    path_buffer = []
    for file_path in file_paths:
        buffer_count += len(file_path) + 1
        path_buffer.append(file_path)
        if buffer_count >= COMMAND_BUFFER_SIZE:
            mimetypes = execute_file_command(path_buffer)
            sizes = [os.path.getsize(path) for path in path_buffer]
            for mimetype, size in zip(mimetypes, sizes):
                mimetype_size_map[mimetype] += size
            path_buffer = []
            buffer_count = BASE_COMMAND_LENGTH
    if path_buffer:
        mimetypes = execute_file_command(path_buffer)
        sizes = [os.path.getsize(path) for path in path_buffer]
        for mimetype, size in zip(mimetypes, sizes):
            mimetype_size_map[mimetype] += size
    total_size = 0
    for mime_type, size in mimetype_size_map.items():
        print(f'{mime_type}: {size}B')
        total_size += size
    print(f'TOTAL SIZE: {total_size}B')
    
if __name__ == '__main__':
    main()