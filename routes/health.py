from fastapi import APIRouter

from services.health_service import (
    check_application,
    check_mongodb,
    check_opensearch
)

router = APIRouter()


@router.get("/health")
def health_check():

    return {
        "application": check_application(),
        "mongodb": check_mongodb(),
        "opensearch": check_opensearch()
    }