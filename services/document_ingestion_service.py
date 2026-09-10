from fastapi import UploadFile
from io import BytesIO
from docx import Document as DocxDocument

from database.models import Document
from database.postgres import SessionLocal
from services.document_loader import extract_pdf_text
from services.chunking_service import chunk_text
from services.opensearch_service import index_chunk


class DocumentIngestionService:

    def extract_text(
        self,
        file_bytes: bytes,
        filename: str
    ):

        extension = filename.split(".")[-1].lower()

        # PDF
        if extension == "pdf":

            pdf_stream = BytesIO(file_bytes)

            return extract_pdf_text(pdf_stream)

        # DOCX
        if extension == "docx":

            doc_stream = BytesIO(file_bytes)

            doc = DocxDocument(doc_stream)

            paragraphs = []

            for paragraph in doc.paragraphs:

                text = paragraph.text.strip()

                if text:
                    paragraphs.append(text)

            return "\n".join(paragraphs)

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    def ingest_document(
        self,
        file_bytes: bytes,
        original_filename: str,
        s3_key: str,
        audience: str
    ):
        """
        Complete ingestion pipeline.

        Steps:
        1. Save metadata
        2. Extract text
        3. Chunk document
        4. Generate embeddings
        5. Index into OpenSearch
        """
        db = SessionLocal()

        try:

            document = Document(
                document_name=original_filename,
                audience=audience,
                workflow="Unknown",
                page_name="Unknown",
                file_path="",
                s3_key=s3_key
            )

            db.add(document)
            db.commit()
            db.refresh(document)

            text = self.extract_text(
                file_bytes=file_bytes,
                filename=original_filename
            )
            chunks = chunk_text(text)
            for chunk in chunks:

                index_chunk(
                    text=chunk,
                    document_id=document.id,
                    document_name=document.document_name,
                    page_name=document.page_name,
                    uploaded_at=document.uploaded_at,
                    audience=document.audience
                )
            print(f"Generated {len(chunks)} chunks")

            return document

        finally:
            db.close()