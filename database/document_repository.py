from datetime import datetime, UTC

from database.mongo_helpers import get_documents_collection


def create_document(
    document_name: str,
    workflow: str,
    page_name: str,
    file_path: str,
    s3_key: str | None,
    audience: str,
):
    collection = get_documents_collection()

    document = {
        "document_name": document_name,
        "workflow": workflow,
        "page_name": page_name,
        "file_path": file_path,
        "s3_key": s3_key,
        "uploaded_at": datetime.now(UTC),
        "audience": audience,
    }

    result = collection.insert_one(document)

    document["_id"] = result.inserted_id

    return document