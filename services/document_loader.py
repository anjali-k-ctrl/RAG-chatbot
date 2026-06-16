from docx import Document as DocxDocument


def extract_docx_text(file_path: str) -> str:
    doc = DocxDocument(file_path)

    text = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)

from pypdf import PdfReader


def extract_pdf_text(file_path: str):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text