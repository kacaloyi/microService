# -*- codeing: utf-8 -*-


def ensure_file_dir_exists(filepath=None, dirpath=None):
    if filepath and isinstance(filepath, str):
        file_dir = os.path.dirname(filepath)
        if file_dir and not os.path.exists(file_dir):
            os.makedirs(file_dir, exist_ok=True)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)