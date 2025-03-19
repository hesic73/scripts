import subprocess
import fire
import os
from loguru import logger


def extract_audio_from_mp4(input_file: str, output_file: str = None, audio_channels: int = 2, audio_rate: int = 44100, audio_bitrate: str = "192k"):
    """
    Extracts audio from an MP4 file and saves it as an MP3 file.

    If no output file is specified, the MP3 file is saved in the same directory with the same name as the input file, but with an .mp3 extension.
    """
    if not output_file:
        # 生成默认的输出文件名
        output_file = os.path.splitext(input_file)[0] + ".mp3"

    command = [
        "ffmpeg",
        "-i", input_file,  # 输入文件
        "-vn",  # 去除视频部分
        "-ar", str(audio_rate),  # 采样率
        "-ac", str(audio_channels),  # 声道数
        "-b:a", audio_bitrate,  # 比特率
        output_file  # 输出文件
    ]

    try:
        logger.info(f"Extracting audio from: {input_file}")
        logger.info(f"Output file: {output_file}")
        logger.info(
            f"Audio Channels: {audio_channels}, Sampling Rate: {audio_rate} Hz, Bitrate: {audio_bitrate}")

        subprocess.run(command, check=True)
        logger.success(f"Audio extracted and saved to {output_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during audio extraction: {e}")


if __name__ == "__main__":
    fire.Fire(extract_audio_from_mp4)
