from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.s3_service import upload_file_to_s3
from services.document_ingestion_service import DocumentIngestionService
from services.unanswered_resolution_service import UnansweredResolutionService
from database.postgres import SessionLocal
from database.models import UnansweredQuestion
from config.settings import settings

from services.s3_service import delete_document_from_s3
from services.opensearch_service import delete_document_chunks

from database.models import Document

router = APIRouter()
document_ingestion_service = DocumentIngestionService()

from io import BytesIO
from enum import Enum

class Audience(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"


@router.post("/upload-knowledge")
async def upload_knowledge(
    file: UploadFile = File(...),
    audience: Audience = Form(...)
):
    audience = audience.value
    # ----------------------------------------
    # READ FILE
    # ----------------------------------------

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    # ----------------------------------------
    # UPLOAD ORIGINAL FILE TO S3
    # ----------------------------------------

    upload_result = upload_file_to_s3(
        BytesIO(file_bytes),
        file.filename,
        audience
    )

    # ----------------------------------------
    # INGEST DOCUMENT
    # ----------------------------------------

    document = document_ingestion_service.ingest_document(
        file_bytes=file_bytes,
        original_filename=file.filename,
        s3_key=upload_result["s3_key"],
        audience=audience
    )

    # ----------------------------------------
    # CHECK UNANSWERED QUESTIONS
    # ----------------------------------------

    resolution_service = UnansweredResolutionService()

    resolved_questions = (
        resolution_service.resolve_after_document_upload(
            document.document_name,
            document.audience
        )
    )

    # ----------------------------------------
    # GET PENDING QUESTION COUNT
    # ----------------------------------------

    db = SessionLocal()

    try:

        pending_count = (
            db.query(UnansweredQuestion)
            .filter(
                UnansweredQuestion.status == "Pending"
            )
            .count()
        )

    finally:

        db.close()

    print(
        f"Document uploaded successfully "
        f"| ID: {document.id} "
        f"| Audience: {audience}"
    )

    return {

        "message": "Document uploaded successfully",

        "document_id": document.id,

        "audience": document.audience,

        **upload_result,

        "resolution_summary": {

            "resolved_count": len(resolved_questions),

            "pending_count": pending_count,

            "resolved_questions": resolved_questions

        }

    }
@router.delete("/documents/{document_id}")
async def delete_document(document_id: int):

    db = SessionLocal()

    try:

        # ----------------------------------------
        # FIND DOCUMENT IN POSTGRESQL
        # ----------------------------------------

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        s3_key = document.s3_key

        print("\n===== DOCUMENT DELETE START =====")
        print("Document ID:", document.id)
        print("Document Name:", document.document_name)
        print("S3 Key:", s3_key)

        # ----------------------------------------
        # STEP 1: DELETE OPENSEARCH CHUNKS
        # ----------------------------------------

        print("\nSTEP 1: Deleting OpenSearch chunks")

        delete_result = delete_document_chunks(
            document_id=document.id
        )

        print("OpenSearch result:", delete_result)

        # ----------------------------------------
        # STEP 2: DELETE S3 FILE
        # ----------------------------------------

        if s3_key:

            print("\nSTEP 2: Deleting S3 object")
            print("S3 Bucket:", settings.AWS_BUCKET_NAME)
            print("S3 Key:", s3_key)

            delete_document_from_s3(s3_key)

            print("S3 object deleted successfully")

        else:

            print("\nSTEP 2: No S3 key found")
            print("Skipping S3 deletion")

        # ----------------------------------------
        # STEP 3: DELETE POSTGRESQL METADATA
        # ----------------------------------------

        print("\nSTEP 3: Deleting PostgreSQL record")

        db.delete(document)
        db.commit()

        print("PostgreSQL record deleted successfully")
        print("===== DOCUMENT DELETE COMPLETE =====\n")

        return {
            "message": "Document deleted successfully",
            "document_id": document_id
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        print(
            f"\nERROR deleting document {document_id}: {repr(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete document"
        )

    finally:
        db.close()