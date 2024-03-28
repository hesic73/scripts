import os
import fitz  # PyMuPDF
import click


def extract_images_from_pdf(pdf_path: str, output_dir: str) -> int:
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Track image count
    img_count = 0

    # Iterate through each page of the PDF
    for page_num in range(len(doc)):
        # Extract images
        images = doc.get_page_images(page_num)

        for image_index, img in enumerate(images):
            # Get the image information
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Construct the image file path
            image_path = os.path.join(output_dir, f"image{page_num + 1}_{image_index + 1}.png")

            # Save the image
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            img_count += 1

    # Close the PDF document
    doc.close()

    return img_count


@click.command()
@click.argument('pdf_file_path', type=click.Path(exists=True))
@click.option('--output_dir', default='.',
              help='Directory to save extracted images. Defaults to current working directory.')
def main(pdf_file_path: str, output_dir: str):
    """Extracts all images from a PDF file and saves them to the specified directory."""

    if not pdf_file_path.lower().endswith('.pdf'):
        click.echo("Error: The specified file does not appear to be a PDF. Please provide a PDF file.")
        return
    img_count = extract_images_from_pdf(pdf_file_path, output_dir)
    click.echo(f"Extracted {img_count} images from {pdf_file_path} to {output_dir}")


if __name__ == "__main__":
    main()
