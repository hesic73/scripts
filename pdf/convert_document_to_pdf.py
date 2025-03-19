"""
Adapted from: https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/examples/convert-document/convert.py
"""

import sys
import os
import fire
import fitz


from typing import Optional
from loguru import logger


def convert(input_file: str, output_dir: Optional[str] = None):

    # output_dir defaults to the current directory if not provided
    if output_dir is None:
        output_dir = os.getcwd()
    else:
        assert os.path.isdir(
            output_dir), f"Output directory {output_dir} does not exist."

    try:
        doc = fitz.open(input_file)

        if doc.is_pdf:
            raise ValueError("The document is already a PDF.")

        # Construct output file path
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}.pdf")

        logger.info(f"Converting '{input_file}' to '{output_file}'")
        pdf_bytes = doc.convert_to_pdf()
        pdf = fitz.open("pdf", pdf_bytes)

        # Handle table of contents
        toc = fitz.utils.get_toc(doc)

        fitz.utils.set_toc(pdf, toc)

        # Handle metadata
        meta = doc.metadata
        if not meta["producer"]:
            meta["producer"] = f"PyMuPDF v{fitz.VersionBind}"
        if not meta["creator"]:
            meta["creator"] = "PyMuPDF PDF converter"

        fitz.utils.set_metadata(pdf, meta)

        # Process links
        link_count, link_skipped = process_links(doc, pdf)

        pdf.save(output_file, garbage=4, deflate=True)
        logger.info(
            f"Conversion completed. Skipped {link_skipped} named links out of {link_count} in input.")
    except Exception as e:
        logger.error(f"Error converting {input_file}: {e}")


def process_links(doc, pdf):
    link_count = 0
    link_skipped = 0
    for pinput in doc.pages():
        links = pinput.get_links()
        link_count += len(links)
        pout = pdf[pinput.number]
        for link in links:
            if link["kind"] == fitz.LINK_NAMED:
                link_skipped += 1
                continue
            pout.insert_link(link)
    return link_count, link_skipped


if __name__ == "__main__":
    fire.Fire(convert)
