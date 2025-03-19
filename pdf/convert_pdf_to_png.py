import fitz  # PyMuPDF
import fire
import os

from typing import Optional
from loguru import logger


def pdf_to_image(pdf_path: str, page_number: int = 0, image_path: Optional[str] = None):
    """
    Convert a specified page of a PDF to an image.

    Args:
        pdf_path (str): Path to the PDF file.
        page_number (int, optional): Page number to convert (default: 0).
        image_path (str, optional): Output image path (default: pdf_basename_{page_number}.png).
    """
    # Open the PDF
    pdf_document = fitz.open(pdf_path)

    # Ensure the page number is valid
    if page_number < 0 or page_number >= len(pdf_document):
        logger.error(
            f"Error: Page number {page_number} is out of range (PDF has {len(pdf_document)} pages).")
        return

    # Extract the page
    page = pdf_document[page_number]

    # Render page as image
    # Scale factor for higher resolution
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

    # Generate default image path if not provided
    if image_path is None:
        pdf_basename = os.path.splitext(os.path.basename(pdf_path))[0]
        image_path = f"{pdf_basename}_{page_number}.png"

    # Save the image
    pix.save(image_path)
    logger.info(f"Saved PDF page {page_number + 1} as image: {image_path}")


if __name__ == "__main__":
    fire.Fire(pdf_to_image)
