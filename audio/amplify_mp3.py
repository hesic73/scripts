import subprocess
from pathlib import Path
from typing import Union
import fire
from loguru import logger

def amplify_mp3(input_path: str, db: Union[int, float]) -> None:
    """
    Amplifies or attenuates the volume of an MP3 file.
    
    :param input_path: Path to the input MP3 file.
    :param db: Decibel change. Positive values increase volume, negative values decrease volume.
    """
    try:
        # Create a Path object from the input path
        input_file = Path(input_path)

        # Generate the output file name by appending the db value
        output_path = input_file.with_stem(f"{input_file.stem}_{db}dB")

        # Construct the ffmpeg command
        command = [
            "ffmpeg",
            "-i", str(input_file),
            "-filter:a", f"volume={db}dB",
            str(output_path)
        ]

        logger.info(f"Executing command: {' '.join(command)}")
        
        # Execute the ffmpeg command
        subprocess.run(command, check=True)

        logger.info(f"Amplification completed successfully. Output: {output_path}")

    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while processing the MP3 file: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fire.Fire(amplify_mp3)

