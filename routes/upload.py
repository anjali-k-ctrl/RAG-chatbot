from enum import Enum
from io import BytesIO

from bson import ObjectId
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from config.settings import settings

from database.mongo_helpers import (
    get_documents_collection,
    get_unanswered_questions_collection
)

from services.s3_service import (
    upload_file_to_s3,
    delete_document_from_s3
)

from services.document_ingestion_service import (
    DocumentIngestionService
)

from services.unanswered_resolution_service import (
    UnansweredResolutionService
)

from services.opensearch_service import (
    delete_document_chunks
)


router = APIRouter()

document_ingestion_service = DocumentIngestionService()


# --------------------------------------------------
# Audience
# --------------------------------------------------

class Audience(str, Enum):

    BUYER = "buyer"
    SELLER = "seller"


# --------------------------------------------------
# Upload Knowledge Document
# --------------------------------------------------

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

    document = (
        document_ingestion_service.ingest_document(
            file_bytes=file_bytes,
            original_filename=file.filename,
            s3_key=upload_result["s3_key"],
            audience=audience
        )
    )

    # ----------------------------------------
    # CHECK UNANSWERED QUESTIONS
    # ----------------------------------------

    resolution_service = (
        UnansweredResolutionService()
    )

    resolved_questions = (
        resolution_service
        .resolve_after_document_upload(
            document["document_name"],
            document["audience"]
        )
    )

    # ----------------------------------------
    # GET PENDING QUESTION COUNT
    # ----------------------------------------

    unanswered_collection = (
        get_unanswered_questions_collection()
    )

    pending_count = (
        unanswered_collection.count_documents({
            "status": "Pending"
        })
    )

    document_id = str(
        document["_id"]
    )

    print(
        f"Document uploaded successfully "
        f"| ID: {document_id} "
        f"| Audience: {audience}"
    )

    return {

        "message":
            "Document uploaded successfully",

        "document_id":
            document_id,

        "audience":
            document["audience"],

        **upload_result,

        "resolution_summary": {

            "resolved_count":
                len(resolved_questions),

            "pending_count":
                pending_count,

            "resolved_questions":
                resolved_questions
        }
    }


# --------------------------------------------------
# Delete Knowledge Document
# --------------------------------------------------

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str
):

    documents_collection = (
        get_documents_collection()
    )

    # ----------------------------------------
    # VALIDATE MONGODB OBJECT ID
    # ----------------------------------------

    try:

        object_id = ObjectId(
            document_id
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    # ----------------------------------------
    # FIND DOCUMENT IN MONGODB
    # ----------------------------------------

    document = (
        documents_collection
        .find_one({
            "_id": object_id
        })
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    s3_key = document.get(
        "s3_key"
    )

    document_name = document.get(
        "document_name"
    )

    print(
        "\n===== DOCUMENT DELETE START ====="
    )

    print(
        "Document ID:",
        document_id
    )

    print(
        "Document Name:",
        document_name
    )

    print(
        "S3 Key:",
        s3_key
    )

    try:

        # ----------------------------------------
        # STEP 1: DELETE OPENSEARCH CHUNKS
        # ----------------------------------------

        print(
            "\nSTEP 1: Deleting OpenSearch chunks"
        )

        delete_result = (
            delete_document_chunks(
                document_id=document_id
            )
        )

        print(
            "OpenSearch result:",
            delete_result
        )

        # ----------------------------------------
        # STEP 2: DELETE S3 FILE
        # ----------------------------------------

        if s3_key:

            print(
                "\nSTEP 2: Deleting S3 object"
            )

            print(
                "S3 Bucket:",
                settings.AWS_BUCKET_NAME
            )

            print(
                "S3 Key:",
                s3_key
            )

            delete_document_from_s3(
                s3_key
            )

            print(
                "S3 object deleted successfully"
            )

        else:

            print(
                "\nSTEP 2: No S3 key found"
            )

            print(
                "Skipping S3 deletion"
            )

        # ----------------------------------------
        # STEP 3: DELETE MONGODB METADATA
        # ----------------------------------------

        print(
            "\nSTEP 3: Deleting MongoDB record"
        )

        delete_result = (
            documents_collection
            .delete_one({
                "_id": object_id
            })
        )

        if delete_result.deleted_count == 0:

            raise Exception(
                "MongoDB document could not be deleted"
            )

        print(
            "MongoDB record deleted successfully"
        )

        print(
            "===== DOCUMENT DELETE COMPLETE =====\n"
        )

        return {

            "message":
                "Document deleted successfully",

            "document_id":
                document_id
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            f"\nERROR deleting document "
            f"{document_id}: {repr(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete document"
        )