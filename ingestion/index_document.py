import os

from database.postgres import SessionLocal
from database.models import Document

from services.document_loader import extract_docx_text


DOCS = [
    ("Start - Title Creations.docx", "title_creation", "start"),
    ("MetaData Title Creations.docx", "title_creation", "metadata"),
    ("Credits Title Creations.docx", "title_creation", "credits"),
    ("Assests Title Creation.docx", "title_creation", "assets"),
    ("Rights Title Creation.docx", "title_creation", "rights"),
    ("Review Title Creations.docx", "title_creation", "review"),
]


db = SessionLocal()

for filename, workflow, page_name in DOCS:

    from services.storage_service import get_document_path

    file_path = get_document_path(filename)
    print(f"Loading: {file_path}")
    text = extract_docx_text(file_path)

    document = Document(
        document_name=filename,
        workflow=workflow,
        page_name=page_name,
        file_path=file_path,
        content=text
    )

    db.add(document)

db.commit()

print("Documents indexed successfully.")