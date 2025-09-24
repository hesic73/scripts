import fitz  # PyMuPDF
from loguru import logger
import fire
import os
from PIL import Image, ImageOps


def trim(pdf_path: str, output_path: str = None, threshold: int = 240):
    """
    Trims the white margins from each page of a PDF file by rendering and thresholding.

    :param pdf_path: Path to the input PDF file.
    :param output_path: Optional path for the trimmed PDF. Defaults to '_trimmed' suffix.
    :param threshold: The pixel value (0-255) to distinguish content from background.
                      Lower values are stricter about what is considered "white".
    """
    if output_path is None:
        base, ext = os.path.splitext(pdf_path)
        output_path = f"{base}_trimmed{ext}"

    logger.info(f"Input PDF: {pdf_path}")
    doc = fitz.open(pdf_path)

    for page in doc:
        dpi = 150
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        gray_img = img.convert("L")
        # Use the threshold argument to make the image pure black and white
        thresholded_img = gray_img.point(lambda x: 0 if x < threshold else 255, "1")

        # Invert the image so the background is black (0), which getbbox can trim.
        inv_img = ImageOps.invert(thresholded_img)

        bbox = inv_img.getbbox()

        if bbox:
            new_crop_box = fitz.Rect(bbox) / zoom
            page.set_cropbox(new_crop_box)

    logger.info(f"Saving trimmed PDF to: {output_path}")
    doc.save(output_path)
    doc.close()


if __name__ == "__main__":
    fire.Fire(trim)
