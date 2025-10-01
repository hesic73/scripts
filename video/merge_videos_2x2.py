import fire
import subprocess
import os
from loguru import logger


def get_video_dimensions(video_path: str):
    """Get the width and height of a video file."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=p=0",
        video_path,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        result_list = result.stdout.strip().split(",")
        if len(result_list) == 2:
            width, height = result_list
        elif len(result_list) == 3:
            assert result_list[2] == ""
            width, height = result_list[:2]
        else:
            raise ValueError(f"Unexpected output from ffprobe: {result.stdout}")
        return int(width), int(height)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting dimensions for {video_path}: {e}")
        return None, None


def get_video_duration(video_path: str) -> float:
    # Return duration in seconds as float
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def merge_videos_2x2(
    video_paths: list[str],
    output_path: str,
    horizontal_padding: int = 0,
    vertical_padding: int = 0,
    background_color: str = "white",
):
    """Merge 4 videos into a 2x2 grid.

    Args:
        video_paths: List of 4 video file paths
        output_path: Output video file path
        horizontal_padding: Padding between videos horizontally (default: 0)
        vertical_padding: Padding between videos vertically (default: 0)
        background_color: Background color for padding (default: "white")
    """

    if len(video_paths) != 4:
        logger.error("Error: Exactly 4 video files are required.")
        return False

    # Check if all videos exist
    for video_path in video_paths:
        if not os.path.exists(video_path):
            logger.error(f"Error: Video file not found: {video_path}")
            return False

    # Get dimensions of first video (assume all are same size)
    width, height = get_video_dimensions(video_paths[0])
    if width is None or height is None:
        return False

    logger.info(f"Video dimensions: {width}x{height}")
    logger.info(f"Horizontal padding: {horizontal_padding}")
    logger.info(f"Vertical padding: {vertical_padding}")
    logger.info(
        f"Output dimensions: {width * 2 + horizontal_padding}x{height * 2 + vertical_padding}"
    )

    # Compute per-video durations and target (longest) duration
    durs = [get_video_duration(p) for p in video_paths]
    max_dur = max(durs)
    pads = [max_dur - d for d in durs]  # seconds to clone at tail for each input
    logger.info(f"Max duration (s): {max_dur:.3f}")

    logger.info(f"Background color: {background_color}")  # new

    # Build ffmpeg command for 2x2 grid with padding
    # Layout:
    # [0][1]
    # [2][3]
    if horizontal_padding > 0 or vertical_padding > 0:
        # Label inputs and pad each stream to the longest duration by cloning the last frame
        filter_complex = (
            f"[0:v]setpts=PTS-STARTPTS, tpad=stop_mode=clone:stop_duration={pads[0]:.6f}[top_left];"
            f"[1:v]setpts=PTS-STARTPTS, tpad=stop_mode=clone:stop_duration={pads[1]:.6f}[top_right];"
            f"[2:v]setpts=PTS-STARTPTS, tpad=stop_mode=clone:stop_duration={pads[2]:.6f}[bottom_left];"
            f"[3:v]setpts=PTS-STARTPTS, tpad=stop_mode=clone:stop_duration={pads[3]:.6f}[bottom_right];"
        )

        if horizontal_padding > 0:
            # Finite black bar with the same total duration; split because each output can be consumed once
            filter_complex += (
                f"color=c={background_color}:s={horizontal_padding}x{height}:d={max_dur:.6f}[hpad];"
                f"[hpad]split=2[hpad_top][hpad_bottom];"
                f"[top_left][hpad_top][top_right]hstack=inputs=3[top];"
                f"[bottom_left][hpad_bottom][bottom_right]hstack=inputs=3[bottom];"
            )
        else:
            filter_complex += (
                f"[top_left][top_right]hstack=inputs=2[top];"
                f"[bottom_left][bottom_right]hstack=inputs=2[bottom];"
            )

        if vertical_padding > 0:
            # Finite horizontal bar with the same total duration
            filter_complex += (
                f"color=c={background_color}:s={width * 2 + horizontal_padding}x{vertical_padding}:d={max_dur:.6f}[vpad];"
                f"[top][vpad][bottom]vstack=inputs=3[v]"
            )
        else:
            filter_complex += f"[top][bottom]vstack=inputs=2[v]"
    else:
        # No-padding path; still pad each stream to the longest duration
        filter_complex = (
            f"[0:v]setpts=PTS-STARTPTS, tpad=stop_mode=clone:stop_duration={pads[0]:.6f}[top_left];"
            f"[1:v]setpts=PTS-STARTPTS, tpad=stop_mode=clone:stop_duration={pads[1]:.6f}[top_right];"
            f"[2:v]setpts=PTS-STARTPTS, tpad=stop_mode=clone:stop_duration={pads[2]:.6f}[bottom_left];"
            f"[3:v]setpts=PTS-STARTPTS, tpad=stop_mode=clone:stop_duration={pads[3]:.6f}[bottom_right];"
            f"[top_left][top_right]hstack=inputs=2[top];"
            f"[bottom_left][bottom_right]hstack=inputs=2[bottom];"
            f"[top][bottom]vstack=inputs=2[v]"
        )

    cmd = [
        "ffmpeg",
        "-i",
        video_paths[0],  # top left
        "-i",
        video_paths[1],  # top right
        "-i",
        video_paths[2],  # bottom left
        "-i",
        video_paths[3],  # bottom right
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-y",  # Overwrite output file if exists
        output_path,
    ]

    logger.info("Running ffmpeg command...")
    logger.debug(
        " ".join(
            cmd[: cmd.index("-filter_complex") + 1]  # up to -filter_complex
            + [f'"{filter_complex}"']  # wrap filter_complex in quotes
            + cmd[cmd.index("-filter_complex") + 2 :]  # remaining arguments
        )
    )

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Successfully created merged video: {output_path}")
            return True
        else:
            logger.error(f"ffmpeg failed with return code {result.returncode}")
            logger.error(f"stderr: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error running ffmpeg: {e}")
        return False


def main(
    video1: str,
    video2: str,
    video3: str,
    video4: str,
    output: str,
    horizontal_padding: int = 0,
    vertical_padding: int = 0,
    background_color: str = "white",
):
    """
    Merge 4 videos into a 2x2 grid.

    Args:
        video1: First video (top left)
        video2: Second video (top right)
        video3: Third video (bottom left)
        video4: Fourth video (bottom right)
        output: Output video file path
        horizontal_padding: Padding between videos horizontally (default: 0)
        vertical_padding: Padding between videos vertically (default: 0)
        background_color: Background color for the grid (default: "white")
    """
    video_paths = [video1, video2, video3, video4]

    _ = merge_videos_2x2(
        video_paths, output, horizontal_padding, vertical_padding, background_color
    )


if __name__ == "__main__":
    fire.Fire(main)
