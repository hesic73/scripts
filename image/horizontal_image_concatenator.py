from typing import Optional
from PIL import Image
import fire
from loguru import logger
import os


def concatenate_images_horizontally(
    left_image_path: str,
    right_image_path: str,
    output_path: Optional[str] = None
) -> None:
    try:
        left_image = Image.open(left_image_path)
        right_image = Image.open(right_image_path)

        # Check if image heights are equal
        if left_image.height != right_image.height:
            logger.error("Images must have the same height to concatenate.")
            return

        # If output_path is not provided, construct default name
        if not output_path:
            left_name, _ = os.path.splitext(os.path.basename(left_image_path))
            right_name, extension = os.path.splitext(
                os.path.basename(right_image_path))
            output_path = f"{left_name}_{right_name}_concatenated{extension}"

        # Compute the total width and ensure same height
        total_width = left_image.width + right_image.width
        height = left_image.height

        # Create new image with the final size
        new_image = Image.new('RGB', (total_width, height))

        # Paste images side by side
        new_image.paste(left_image, (0, 0))
        new_image.paste(right_image, (left_image.width, 0))

        # Save the concatenated image
        new_image.save(output_path)
        logger.info(
            f"The images have been concatenated and saved to {output_path}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    # Fire's entry point for CLI
    fire.Fire(concatenate_images_horizontally)
