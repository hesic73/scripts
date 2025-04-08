import fitz  # PyMuPDF
import fire
from pathlib import Path
from loguru import logger

def extract_pages(input_path: str, pages: list[int], output_path: str = None):
    input_pdf = Path(input_path)
    if not input_pdf.exists():
        logger.error(f"Input file does not exist: {input_pdf}")
        return

    # Default output path if none provided
    if output_path is None:
        output_pdf = input_pdf.with_name(f"{input_pdf.stem}_extracted{input_pdf.suffix}")
    else:
        output_pdf = Path(output_path)

    # Ask user for confirmation if file exists
    if output_pdf.exists():
        confirm = input(f"Output file '{output_pdf}' already exists. Overwrite? [y/N]: ").strip().lower()
        if confirm != "y":
            logger.info("Operation cancelled by user.")
            return

    try:
        doc = fitz.open(str(input_pdf))
        new_doc = fitz.open()

        logger.info(f"Extracting pages {pages} from '{input_pdf.name}'")

        for page_number in pages:
            if 0 <= page_number < len(doc):
                new_doc.insert_pdf(doc, from_page=page_number, to_page=page_number)
            else:
                logger.warning(f"Page number out of range: {page_number}")

        new_doc.save(str(output_pdf))
        logger.success(f"Extracted PDF saved to: {output_pdf}")
    except Exception as e:
        logger.exception("Failed during extraction")

if __name__ == "__main__":
    fire.Fire(extract_pages)

