# app/utils/pdf_extractor.py
"""
Utility module for extracting plain text from PDF files using PyMuPDF (fitz).

The module provides:
- ``PDFExtractionError`` – custom exception for extraction failures.
- ``extract_text_from_pdf(path: str) -> str`` – reads a PDF from ``path`` and returns the concatenated
  textual content of all pages. It raises ``PDFExtractionError`` for empty PDFs, corrupt files,
  or any other issue encountered during parsing.

All functions are deliberately simple and have extensive docstrings to aid beginners.
"""

import fitz  # PyMuPDF – provides efficient PDF handling
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Raised when PDF text extraction fails.

    The exception carries a human‑readable message that explains why the extraction
    could not be performed (e.g., corrupted file, empty document, unsupported format).
    """

    pass


def extract_text_from_pdf(file_path: str) -> str:
    """Extract plain text from a PDF file.

    Parameters
    ----------
    file_path: str
        Absolute or relative path to the PDF file on disk.

    Returns
    -------
    str
        Concatenated text of **all** pages in the document. If the PDF contains no
        extractable text, an empty string is returned.

    Raises
    ------
    PDFExtractionError
        If the file cannot be opened, is not a valid PDF, or any other error occurs.
    """

    pdf_path = Path(file_path)
    if not pdf_path.exists():
        raise PDFExtractionError(f"File not found: {file_path}")

    try:
        # "fitz.open" automatically detects the file type and raises an exception
        # for corrupted PDFs. We wrap it to provide a controlled error type.
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        logger.error("Failed to open PDF %s: %s", file_path, exc)
        raise PDFExtractionError(f"Unable to open PDF file: {exc}") from exc

    if doc.page_count == 0:
        raise PDFExtractionError("PDF contains no pages.")

    full_text_parts = []
    for page_number in range(doc.page_count):
        try:
            page = doc.load_page(page_number)
            text = page.get_text("text")  # plain text extraction
            full_text_parts.append(text)
        except Exception as exc:
            logger.error("Error extracting page %d from %s: %s", page_number + 1, file_path, exc)
            raise PDFExtractionError(
                f"Failed to extract text from page {page_number + 1}: {exc}"
            ) from exc

    doc.close()

    extracted_text = "\n".join(full_text_parts).strip()
    if not extracted_text:
        # The PDF is readable but contains no extractable text (e.g., scanned images).
        raise PDFExtractionError("No extractable text found in PDF.")

    logger.debug("Extracted %d characters of text from %s", len(extracted_text), file_path)
    return extracted_text
