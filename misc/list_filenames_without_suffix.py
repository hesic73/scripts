from fire import Fire

import os


def list_filenames_without_suffix(dir_path: str):
    """
    List all filenames (without suffix) in the given directory.

    :param dir_path: Path to the directory
    :return: List of filenames without suffix
    """
    if not os.path.isdir(dir_path):
        raise ValueError(f"Invalid directory path: {dir_path}")

    filenames = [
        os.path.splitext(f)[0] for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f))
    ]
    return filenames


if __name__ == "__main__":
    Fire(list_filenames_without_suffix)
