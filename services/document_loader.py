import re
from pypdf import PdfReader



def extract_pdf_text(file_path: str):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    # Clean whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove repeated spaces
    text = re.sub(r" +", " ", text)

    return text.strip()