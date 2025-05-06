from typing import Optional
import subprocess
import os
import fire
from loguru import logger


def change_video_speed(
    input_path: str,
    output_path: Optional[str] = None,
    speed_factor: float = 0.50,
    font_path: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    fontsize: int = 64,
) -> None:
    """
    Change video playback speed and overlay the speed factor in the bottom right corner.

    Args:
        input_path: Path to the input video file.
        output_path: Path to the output video file.
        speed_factor: Playback speed (e.g., 0.25 = 4x slower, 2.0 = 2x faster).
        font_path: Path to a .ttf font file to use for the overlay text.
        fontsize: Font size for the speed factor overlay text.
    """
    if not os.path.exists(input_path):
        logger.error(f"Input file '{input_path}' does not exist.")
        return

    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_x{speed_factor:.2f}{ext}"

    text = f"× {speed_factor:.2f}"
    setpts = f"setpts={1/speed_factor}*PTS"

    # Prepare atempo filters: must be between 0.5 and 2.0
    atempo_filters = []
    remaining = speed_factor
    while remaining < 0.5 or remaining > 2.0:
        if remaining < 0.5:
            atempo_filters.append("atempo=0.5")
            remaining /= 0.5
        else:
            atempo_filters.append("atempo=2.0")
            remaining /= 2.0
    atempo_filters.append(f"atempo={remaining:.4f}")
    atempo = ",".join(atempo_filters)

    logger.info(
        f"Changing speed to {speed_factor}x, overlaying text '{text}' with font size {fontsize}")

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf",
        f"{setpts},drawtext=fontfile={font_path}:text='{text}':"
        f"fontcolor=white:fontsize={fontsize}:x=w-tw-10:y=h-th-10",
        "-af", atempo,
        "-y",
        output_path
    ]

    logger.info("Running ffmpeg command...")
    logger.debug(" ".join(cmd))
    subprocess.run(cmd, check=True)
    logger.success(f"Output written to {output_path}")


def main():
    fire.Fire(change_video_speed)


if __name__ == "__main__":
    main()
