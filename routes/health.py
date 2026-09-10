from fastapi import APIRouter

from services.health_service import (
    check_application,
    check_postgres,
    check_opensearch
)

router = APIRouter()


@router.get("/health")
def health():

    return {
        "application": check_application(),
        "postgres": check_postgres(),
        "opensearch": check_opensearch()
    }