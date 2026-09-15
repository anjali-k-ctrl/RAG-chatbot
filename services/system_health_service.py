from datetime import datetime, UTC

from database.mongo_helpers import get_system_health_logs_collection


def log_system_health(
    service: str,
    status: str,
    question: str = None,
    page_name: str = None,
    error: str = None,
    retry_count: int = 0,
    circuit_open: bool = False,
    retrieval_source: str = None,
    response_time_ms: float = None
):
    collection = get_system_health_logs_collection()

    log = {
        "timestamp": datetime.now(UTC),
        "service": service,
        "status": status,
        "question": question,
        "page_name": page_name,
        "error": error,
        "retry_count": retry_count,
        "circuit_open": circuit_open,
        "retrieval_source": retrieval_source,
        "response_time_ms": response_time_ms
    }

    collection.insert_one(log)