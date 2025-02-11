import click
import subprocess
import os

from typing import Optional


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
    click.echo(f"Conversion complete: {output_path}")


@click.command()
@click.argument("input_path")
@click.argument("output_path", required=False)
def main(input_path, output_path):
    convert_mov_to_mp4(input_path, output_path)


if __name__ == "__main__":
    main()
