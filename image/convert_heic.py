import os
import fire
import pyheif
from PIL import Image
from loguru import logger


def convert_images(input_dir: str, output_dir: str, output_format: str = "jpg"):
    """
    Convert all HEIC images in input_dir to PNG or JPG in output_dir.

    :param input_dir: Directory containing HEIC images.
    :param output_dir: Directory to save converted images.
    :param output_format: Output format, "png" or "jpg". Default is "jpg".
    """
    output_format = output_format.lower()
    if output_format not in ["png", "jpg", "jpeg"]:
        raise ValueError("Output format must be 'png' or 'jpg'.")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    logger.info(
        f"Starting conversion: {input_dir} → {output_dir} (Format: {output_format})")

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".heic"):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(
                filename)[0] + f".{output_format}"
            output_path = os.path.join(output_dir, output_filename)

            try:
                # Read the HEIC file
                heif_file = pyheif.read(input_path)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride,
                )

                # Convert and save
                if output_format in ["jpg", "jpeg"]:
                    # JPG does not support alpha channel
                    image = image.convert("RGB")
                    image.save(output_path, "JPEG", quality=95)
                else:
                    image.save(output_path, "PNG")

                logger.info(f"Converted: {input_path} to {output_path}")

            except Exception as e:
                logger.error(f"Failed to convert {input_path}: {e}")

    logger.success("Batch conversion completed!")


if __name__ == "__main__":
    fire.Fire(convert_images)
