import fire
import subprocess
import os
import ffmpeg
from typing import Optional
from loguru import logger


def crop_video(input_path: str, output_path: Optional[str] = None, offset: int = 0, aspect_ratio: str = "16:9"):
    """
    裁剪视频，使其宽度最大化，并调整高度为 width * (h / w)，居中裁剪，支持高度方向的偏移。

    :param input_path: 输入视频路径
    :param output_path: 输出视频路径（可选，默认为输入文件名加 `_cropped`）
    :param offset: 高度方向上的偏移（可选，默认 0）
    :param aspect_ratio: 目标宽高比，格式 "w:h"（可选，默认 "16:9"）
    """
    if not output_path:
        base_name, ext = os.path.splitext(input_path)
        output_path = f"{base_name}_cropped{ext}"

    # 解析宽高比
    try:
        aspect_w, aspect_h = map(int, aspect_ratio.split(":"))
        aspect_ratio_value = aspect_h / aspect_w
    except ValueError:
        logger.error("宽高比格式错误，请使用 'w:h' 形式，例如 '16:9'")
        return

    # 获取输入视频的原始宽高
    probe = ffmpeg.probe(input_path)
    video_stream = next(
        stream for stream in probe["streams"] if stream["codec_type"] == "video"
    )
    width = int(video_stream["width"])
    height = int(video_stream["height"])

    # 计算目标高度
    new_height = int(width * aspect_ratio_value)

    if new_height > height:
        logger.error("目标高度超出原视频高度，无法裁剪")
        return

    # 计算裁剪起点（y 方向居中，考虑 offset）
    y_start = (height - new_height) // 2 + offset

    # 确保 y_start 不越界
    y_start = max(0, min(y_start, height - new_height))

    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", f"crop={width}:{new_height}:0:{y_start}",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]

    subprocess.run(command, check=True)

    logger.info(f"Cropped {input_path} -> {output_path}")


if __name__ == "__main__":
    fire.Fire(crop_video)
