from fastapi import APIRouter
from services.analytics_service import ( get_analytics )
from services.analytics_service import ( get_top_unanswered_questions )
from services.analytics_service import ( get_recent_unanswered_questions )
from services.analytics_service import ( get_daily_report )
from services.analytics_service import ( get_weekly_report )
from database.models import IrrelevantQuestion
from database.postgres import SessionLocal
from database.models import UserFeedback

router = APIRouter()

@router.get("/analytics")
def analytics():
    return get_analytics()

@router.get("/top-unanswered-questions")
def top_unanswered_questions():
    return get_top_unanswered_questions()

@router.get("/recent-unanswered-questions")
def recent_unanswered_questions():
    return get_recent_unanswered_questions()

from fastapi import Query


@router.get("/daily-report")
def daily_report(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None)
):
    return get_daily_report(
        from_date,
        to_date
    )


@router.get("/weekly-report")
def weekly_report(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None)
):
    return get_weekly_report(
        from_date,
        to_date
    )

from fastapi import Query

@router.get("/recent-user-feedback")
def recent_user_feedback(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50)
):

    db = SessionLocal()

    try:

        total = db.query(UserFeedback).count()

        feedback = (
            db.query(UserFeedback)
            .order_by(
                UserFeedback.created_at.desc()
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [
                {
                    "id": f.id,
                    "question": f.question,
                    "chatbot_answer": f.chatbot_answer,
                    "helpful": f.helpful,
                    "category": f.feedback_category,
                    "feedback": f.feedback,
                    "reviewed": f.reviewed,
                    "created_at": f.created_at.strftime("%Y-%m-%d %H:%M")
                }
                for f in feedback
            ],
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }

    finally:
        db.close()

from datetime import datetime
from fastapi import HTTPException
@router.post("/feedback/{feedback_id}/review")
def mark_feedback_reviewed(feedback_id: int):

    db = SessionLocal()

    try:

        feedback = (
            db.query(UserFeedback)
            .filter(UserFeedback.id == feedback_id)
            .first()
        )

        if not feedback:
            raise HTTPException(
                status_code=404,
                detail="Feedback not found"
            )

        feedback.reviewed = True
        feedback.reviewed_at = datetime.utcnow()

        db.commit()

        return {
            "message": "Feedback marked as reviewed."
        }

    finally:

        db.close()

from fastapi import Query
@router.get("/recent-irrelevant-questions")

def recent_irrelevant_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50)
):

    db = SessionLocal()

    try:

        total = db.query(IrrelevantQuestion).count()

        questions = (
            db.query(IrrelevantQuestion)
            .order_by(IrrelevantQuestion.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [
                {
                    "question": q.question,
                    "reason": q.reason,
                    "created_at": q.created_at.strftime("%Y-%m-%d %H:%M")
                }
                for q in questions
            ],
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }

    finally:
        db.close()