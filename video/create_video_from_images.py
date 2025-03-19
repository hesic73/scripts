import cv2
import os
import fire
from datetime import datetime
from typing import Optional, Callable, Any
from loguru import logger


def create_video_from_images(image_dir: str, output_path: str, fps: float = 10, key: Optional[Callable[[str], Any]] = None):
    # 获取目录中的所有图片文件
    files = [f for f in os.listdir(
        image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    # 根据自定义比较函数或按字母顺序排序
    if key:
        files.sort(key=key)
    else:
        files.sort()

    # 确保文件列表不为空
    if not files:
        logger.error("No image files found in the directory.")
        return

    # 读取第一张图片以获取尺寸信息
    first_frame_path = os.path.join(image_dir, files[0])
    frame = cv2.imread(first_frame_path)
    if frame is None:
        logger.error(f"Error reading the first image file: {first_frame_path}")
        return
    height, width, layers = frame.shape
    size = (width, height)

    # 定义编解码器并创建 VideoWriter 对象
    out = cv2.VideoWriter(
        output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    for filename in files:
        full_path = os.path.join(image_dir, filename)
        frame = cv2.imread(full_path)
        if frame is None:
            logger.warning(
                f"Skipping file {filename} as it is not a valid image")
            continue
        # 确保所有图片大小一致
        if (frame.shape[1], frame.shape[0]) != size:
            frame = cv2.resize(frame, size)
        out.write(frame)

    # 释放资源
    out.release()
    cv2.destroyAllWindows()
    logger.success(f"Video saved to {output_path}")


def main(image_dir: str, output_path: Optional[str] = None, fps: float = 10):
    # 清理 image_dir 以移除尾部的斜杠
    image_dir = image_dir.rstrip('/')

    # 确定默认的输出路径
    if output_path is None:
        dir_name = os.path.basename(image_dir)
        default_path = f"{dir_name}.mp4"
        if os.path.exists(default_path):
            current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            default_path = f"./video_{current_time}.mp4"
        output_path = default_path

    logger.info(f"Processing images from: {image_dir}")
    logger.info(f"Output video path: {output_path}")
    logger.info(f"FPS: {fps}")

    # 生成视频
    create_video_from_images(image_dir, output_path,
                             fps, key=lambda x: int(os.path.splitext(x)[0]))


if __name__ == '__main__':
    fire.Fire(main)
