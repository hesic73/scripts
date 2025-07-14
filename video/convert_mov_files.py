import fire
import subprocess
import os

from typing import Optional

from loguru import logger
from tqdm import tqdm


def convert_mov_files(input_path: str, output_dir: Optional[str] = None, verbose: bool = False):
    """
    Converts .mov files from a specified input directory to .mp4 format.

    Args:
        input_path (str): The path to the directory containing .mov files.
        output_dir (Optional[str]): The directory where converted .mp4 files will be saved.
                                     If not provided, files will be saved in the input directory.
        verbose (bool): If True, ffmpeg's detailed output will be printed. Otherwise, it will be suppressed.
    """
    if not os.path.isdir(input_path):
        raise Exception(
            f"Error: Input path '{input_path}' is not a valid directory.")

    if output_dir:
        if os.path.exists(output_dir):
            if not os.path.isdir(output_dir):
                raise Exception(f"Error: '{output_dir}' is not a directory.")
            if os.listdir(output_dir):
                confirmation = input(
                    f"Output directory '{output_dir}' is not empty. Continue? (y/N): ")
                if confirmation.lower() != 'y':
                    logger.info("Operation cancelled by user.")
                    return
        else:
            os.makedirs(output_dir)

    mov_extensions = {".mov", ".MOV"}
    mov_files_to_convert = []

    for filename in os.listdir(input_path):
        _, ext = os.path.splitext(filename)
        if ext in mov_extensions:
            mov_files_to_convert.append(filename)

    if not mov_files_to_convert:
        logger.info(f"No .mov files found in '{input_path}'.")
        return

    for filename in tqdm(mov_files_to_convert, desc="Converting MOV to MP4"):
        full_input_path = os.path.join(input_path, filename)

        if output_dir:
            base_name, _ = os.path.splitext(filename)
            full_output_path = os.path.join(output_dir, f"{base_name}.mp4")
        else:
            base_name, _ = os.path.splitext(full_input_path)
            full_output_path = f"{base_name}.mp4"

        command = [
            "ffmpeg", "-i", full_input_path,
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            full_output_path
        ]

        if not verbose:
            subprocess.run(command, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.run(command, check=True)

        logger.info(f"Converted {full_input_path} to {full_output_path}")


if __name__ == "__main__":
    fire.Fire(convert_mov_files)
