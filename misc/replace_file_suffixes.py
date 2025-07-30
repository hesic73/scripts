import os
import fire
from loguru import logger

def replace_file_suffixes(directory: str, old_suffix: str, new_suffix: str):
    """
    Replaces the suffix of all files under <directory> from old_suffix to new_suffix.

    Args:
        directory (str): The target directory.
        old_suffix (str): The suffix to be replaced.
        new_suffix (str): The new suffix.
    """
    logger.info(f"Starting file suffix replacement operation in directory: {directory}")
    logger.info(f"Replacing files with suffix '{old_suffix}' with '{new_suffix}'")

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(old_suffix):
                old_filepath = os.path.join(root, filename)
                new_filename = filename[:-len(old_suffix)] + new_suffix
                new_filepath = os.path.join(root, new_filename)

                os.rename(old_filepath, new_filepath)
                logger.info(f"Renamed: {old_filepath} -> {new_filepath}")

    logger.info("File suffix replacement operation completed.")

if __name__ == "__main__":
    fire.Fire(replace_file_suffixes)