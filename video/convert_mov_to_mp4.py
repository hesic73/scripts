import fire
import subprocess
import os

from typing import Optional

from loguru import logger


def convert_mov_to_mp4(input_path: str, output_path: Optional[str] = None):
    if not output_path:
        base_name, _ = os.path.splitext(input_path)
        output_path = f"{base_name}.mp4"

    command = [
        "ffmpeg", "-i", input_path,
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]

    subprocess.run(command, check=True)

    logger.info(f"Converted {input_path} to {output_path}")


if __name__ == "__main__":
    fire.Fire(convert_mov_to_mp4)
