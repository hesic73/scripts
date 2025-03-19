import os
from PIL import Image
import fire
from loguru import logger


def is_16_9_ratio(image: Image.Image) -> bool:
    """Check if the image has a 16:9 aspect ratio."""
    width, height = image.size
    return width / height == 16 / 9


def center_crop_16_9(image: Image.Image) -> Image.Image:
    """Center crop the image to a 16:9 aspect ratio, keeping the same width."""
    width, height = image.size
    target_height = int(width * 9 / 16)
    if height > target_height:
        top = (height - target_height) // 2
        bottom = top + target_height
        return image.crop((0, top, width, bottom))
    return image


def crop_or_copy_16_9_images(input_dir: str, output_dir: str = os.getcwd()):
    """Process images in the input directory, copying or cropping to 16:9 ratio as needed."""
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)
        if not os.path.isfile(filepath):
            continue

        with Image.open(filepath) as img:
            if is_16_9_ratio(img):
                output_path = os.path.join(output_dir, filename)
                img.save(output_path)
                logger.info(f"Copied: {filename}")
            else:
                cropped_img = center_crop_16_9(img)
                output_path = os.path.join(output_dir, filename)
                cropped_img.save(output_path)
                logger.success(f"Cropped and saved: {filename}")


if __name__ == '__main__':
    fire.Fire(crop_or_copy_16_9_images)
