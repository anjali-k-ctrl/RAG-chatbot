import os
from services.s3_service import upload_document_to_s3
from database.postgres import SessionLocal
from database.models import Document
from datetime import datetime


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

    s3_key = upload_document_to_s3(file_path)

    print(f"Uploaded to S3: {s3_key}")

    document = Document(
        document_name=filename,
        workflow=workflow,
        page_name=page_name,
        file_path=file_path,
        uploaded_at=datetime.utcnow(),
        s3_key=s3_key
    )

    db.add(document)

db.commit()

print("Documents indexed successfully.")