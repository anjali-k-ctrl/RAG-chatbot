from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from docx import Document


def extract_document_text(file_bytes: bytes, filename: str) -> str:

    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        text = extract_pdf_text(file_bytes)

    elif extension == ".docx":
        text = extract_docx_text(file_bytes)

    else:
        raise ValueError("Only PDF and DOCX files are supported.")

    text = text.strip()

    if not text:
        raise ValueError("No readable text found in the document.")

    return text


def extract_pdf_text(file_bytes: bytes) -> str:

    reader = PdfReader(BytesIO(file_bytes))

    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages)


def extract_docx_text(file_bytes: bytes) -> str:

    document = Document(BytesIO(file_bytes))

    paragraphs = [
        p.text for p in document.paragraphs if p.text.strip()
    ]

    for table in document.tables:
        for row in table.rows:
            row_text = [
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            ]

            if row_text:
                paragraphs.append(" | ".join(row_text))

    return "\n".join(paragraphs)