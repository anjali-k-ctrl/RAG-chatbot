from database.postgres import SessionLocal
from database.models import FailedRetrievalRequest


def save_failed_request(
    question: str,
    page_name: str = None,
    error: str = None,
    service: str = "OpenSearch"
):

    db = SessionLocal()

    try:

        failed_request = FailedRetrievalRequest(
            question=question,
            page_name=page_name,
            error=error,
            service=service
        )

        db.add(failed_request)
        db.commit()

    finally:

        db.close()