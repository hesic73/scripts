"""
Adapted from: https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/examples/convert-document/convert.py
"""

import sys
import os
import click
import fitz


@click.command()
@click.argument('input_file')
@click.option('--output-dir', default='.',
              help='Directory to save the output PDF file. Defaults to the current working directory.')
def convert(input_file, output_dir):
    try:
        doc = fitz.open(input_file)

        if doc.is_pdf:
            raise ValueError("The document is already a PDF.")

        # Construct output file path
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}.pdf")

        print(f"Converting '{input_file}' to '{output_file}'")
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
        print(f"Conversion completed. Skipped {link_skipped} named links out of {link_count} in input.")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


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
    convert()
