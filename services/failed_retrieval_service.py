from datetime import datetime, UTC

from database.mongo_helpers import (
    get_failed_retrieval_requests_collection
)


def save_failed_request(
    question: str,
    page_name: str = None,
    error: str = None,
    service: str = "OpenSearch"
):
    collection = get_failed_retrieval_requests_collection()

    failed_request = {
        "question": question,
        "page_name": page_name,
        "error": error,
        "service": service,
        "created_at": datetime.now(UTC),
        "resolved": False
    }

    collection.insert_one(failed_request)