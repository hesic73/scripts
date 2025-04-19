import os
import subprocess
from typing import Optional
from loguru import logger
import fire


def compress_directory(directory_path: str, output_filename: Optional[str] = None) -> None:
    """
    Compresses the specified directory into a .tar.gz file.
    The output filename defaults to {directory_name}.tar.gz if not provided.

    :param directory_path: Path to the directory to compress.
    :param output_filename: Optional; The name of the output .tar.gz file.
    """

    # Normalize and clean up the directory path
    directory_path = os.path.normpath(directory_path)

    # Check if the directory exists
    if not os.path.isdir(directory_path):
        logger.error(f"Directory '{directory_path}' does not exist.")
        return

    # Generate the default output filename if none is provided
    if not output_filename:
        directory_name = os.path.basename(directory_path)
        output_filename = f"{directory_name}.tar.gz"

    # Check if the output file already exists
    if os.path.exists(output_filename):
        response = input(
            f"'{output_filename}' already exists. Do you want to overwrite it? (y/n): ").strip().lower()
        if response != 'y':
            logger.info("Operation cancelled by the user.")
            return
        else:
            logger.info(f"Overwriting existing file '{output_filename}'.")

    # Composing the tar command
    tar_command = ['tar', '-czvf', output_filename, '-C',
                   os.path.dirname(directory_path), os.path.basename(directory_path)]

    # Run the tar command using subprocess
    try:
        logger.info(
            f"Compressing directory '{directory_path}' to '{output_filename}'.")
        subprocess.run(tar_command, check=True)
        logger.info(f"Successfully created '{output_filename}'.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to compress directory: {e}")


if __name__ == "__main__":
    fire.Fire(compress_directory)
