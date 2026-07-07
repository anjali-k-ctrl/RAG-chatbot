from fastapi import APIRouter

from database.postgres import SessionLocal
from database.models import UnansweredQuestion
from services.analytics_service import ( get_weekly_report )

router = APIRouter()


@router.get("/knowledge-gaps")
def get_knowledge_gaps():

    db = SessionLocal()

    try:

        questions = (
            db.query(UnansweredQuestion)
            .order_by(UnansweredQuestion.created_at.desc())
            .all()
        )

        return [
            {
                "id": q.id,
                "question": q.question,
                "page_name": q.page_name,
                "source_document": q.source_document,
                "created_at": q.created_at
            }
            for q in questions
        ]

    finally:
        db.close()

