import os
import fitz  # PyMuPDF
import fire
from loguru import logger


def extract_images_from_pdf(pdf_path: str, output_dir: str) -> int:
    """
    Extracts all images from a PDF file and saves them to the specified directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    doc = fitz.open(pdf_path)
    img_count = 0

    for page_num in range(len(doc)):
        images = doc.get_page_images(page_num)
        for image_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_path = os.path.join(
                output_dir, f"image{page_num + 1}_{image_index + 1}.png")

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            img_count += 1
            logger.info(f"Extracted image: {image_path}")

    doc.close()
    logger.success(
        f"Extracted {img_count} images from {pdf_path} to {output_dir}")
    return img_count


def main(pdf_file_path: str, output_dir: str = "."):
    """
    Extracts all images from a PDF file and saves them to the specified directory.
    """
    if not pdf_file_path.lower().endswith(".pdf"):
        logger.error(
            "The specified file does not appear to be a PDF. Please provide a valid PDF file.")
        return

    extract_images_from_pdf(pdf_file_path, output_dir)


if __name__ == "__main__":
    fire.Fire(main)
