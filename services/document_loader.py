from docx import Document as DocxDocument


def extract_docx_text(file_path: str) -> str:
    doc = DocxDocument(file_path)

    text = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)