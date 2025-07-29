#! /usr/bin/env python3
# vim:fenc=utf-8
#
# Copyright © 2025 youfa <vsyfar@gmail.com>
#
# Distributed under terms of the GPLv2 license.

"""

"""

import argparse
import io
import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def add_hidden_text_to_pdf(
    input_pdf_path: str, output_pdf_path: str, hidden_string: str
):
    """
    Embeds a transparent, hidden string into each page of a PDF file
    without altering the original visible content.

    The hidden text is placed at the top-left corner of each page,
    rendered with full transparency (alpha=0), making it invisible
    to human readers but still parsable by text extraction tools.

    Args:
        input_pdf_path (str): The file path of the input PDF.
        output_pdf_path (str): The file path where the new PDF with
                                hidden text will be saved.
        hidden_string (str): The string to be hidden within the PDF.
    """
    try:
        # 1. Read the original PDF
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()

        # 2. Iterate through each page of the original PDF
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            # Get page dimensions to create an overlay of the same size
            page_width = page.mediabox.width
            page_height = page.mediabox.height

            # 3. Create a PDF overlay containing the transparent text
            # Use BytesIO to create an in-memory PDF, avoiding temporary files
            packet = io.BytesIO()
            # Initialize a ReportLab canvas with the same dimensions as the PDF page
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))

            # Set text fill color to completely transparent (RGBA: Red, Green, Blue, Alpha)
            # An Alpha (A) value of 0 means fully transparent.
            can.setFillColorRGB(0, 0, 0, alpha=0)

            # Draw the hidden string onto the canvas.
            # It's typically placed in a corner to ensure it doesn't interfere
            # with existing content but is still parsable.
            # Placed at the top-left corner, 10pt from the edges.
            can.drawString(10, page_height - 10, hidden_string)
            can.save()  # Save the canvas content to the BytesIO object

            # Read the transparent text PDF from the BytesIO object
            hidden_text_pdf = PdfReader(io.BytesIO(packet.getvalue()))
            # Get the first (and only) page from the transparent text PDF
            hidden_text_page = hidden_text_pdf.pages[0]

            # 4. Merge the original page with the transparent text overlay
            page.merge_page(hidden_text_page)
            # Add the modified page to the writer
            writer.add_page(page)

        # 5. Save the new PDF file
        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)

        print(
            f"Successfully added hidden text to '{input_pdf_path}'. "
            f"New file saved as '{output_pdf_path}'."
        )

    except FileNotFoundError:
        print(
            f"Error: Input PDF file not found at '{input_pdf_path}'. "
            "Please ensure the path is correct."
        )
    except Exception as e:
        print(f"An error occurred while processing the PDF: {e}")


def main():
    """
    Main function to parse command-line arguments and call the
    add_hidden_text_to_pdf function.
    """
    parser = argparse.ArgumentParser(
        description="Embeds hidden, transparent text into a PDF file."
    )
    parser.add_argument(
        "-i", "--input", type=str, required=True, help="Path to the input PDF file."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Path where the new PDF file with hidden text will be saved.",
    )
    parser.add_argument(
        "-t",
        "--text",
        type=str,
        required=True,
        help="The string of text to be hidden within the PDF.",
    )

    args = parser.parse_args()

    # Create a simple test PDF file if the input file does not exist
    # This is useful for initial testing without needing a pre-existing PDF.
    if not os.path.exists(args.input):
        print(
            f"Input PDF '{args.input}' not found. Creating a dummy PDF for testing..."
        )
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            with open(args.input, "wb") as f:
                c = canvas.Canvas(f, pagesize=letter)
                c.drawString(100, 750, "This is a test document.")
                c.drawString(100, 730, "Original visible content.")
                c.save()
            print(f"Test file created at: {args.input}")
        except Exception as e:
            print(f"Error creating test PDF: {e}")
            print("Please ensure you have 'reportlab' installed and write permissions.")
            return  # Exit if dummy PDF creation fails

    add_hidden_text_to_pdf(args.input, args.output, args.text)

    print("\n--- Verification Instructions ---")
    print(
        f"Open '{args.output}' with a PDF reader; you should not see the hidden text."
    )
    print(
        "Then, try using a PDF parsing tool (e.g., 'pdfminer.six' or PyPDF2's text extraction)"
    )
    print(f"to read the content of '{args.output}'. You should find the hidden string.")


if __name__ == "__main__":
    # This block is for direct execution of the script, e.g., `python main.py`
    # It will use the `main` function to handle argument parsing.
    # Note: When installed via pip, the entry point `pdf-hider` will call `main()` directly.
    import os  # Import os here for the exists check in this specific context

    main()
