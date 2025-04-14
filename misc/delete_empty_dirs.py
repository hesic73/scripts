import os
from typing import List
import fire
from loguru import logger


def delete_empty_dirs(base_dir: str) -> None:
    """
    Delete all empty directories under the given directory recursively.

    Args:
    - base_dir: The path to the base directory to start searching for empty directories.
    """
    logger.info(f"Starting to delete empty directories under {base_dir}")

    # Iteratively traverse the directory tree
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                # Remove the directory if it is empty
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    logger.info(f"Deleted empty directory: {dir_path}")
            except Exception as e:
                logger.error(f"Failed to delete {dir_path}: {e}")

    logger.info(f"Completed deletion of empty directories under {base_dir}")


if __name__ == "__main__":
    fire.Fire(delete_empty_dirs)
