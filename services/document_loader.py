import re
from pypdf import PdfReader


def extract_pdf_text(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r" +", " ", text)

    return text.strip()