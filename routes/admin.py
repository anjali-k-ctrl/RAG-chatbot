from fastapi import APIRouter
from sqlalchemy import func
from database.models import UserFeedback
from database.postgres import SessionLocal
from database.models import UnansweredQuestion
from services.analytics_service import ( get_weekly_report )
from fastapi import APIRouter
from database.postgres import SessionLocal
from database.models import UnansweredQuestion
from database.models import Document, UnansweredQuestion

from fastapi import APIRouter, HTTPException

from services.chatbot_settings_service import (
    get_chatbot_status,
    set_chatbot_status
)

router = APIRouter()
@router.get("/chatbot/status")
def chatbot_status():

    return {
        "enabled": get_chatbot_status()
    }
@router.put("/chatbot/status")
def update_chatbot_status(enabled: bool):

    updated_status = set_chatbot_status(
        enabled
    )

    return {
        "message": "Chatbot status updated successfully",
        "enabled": updated_status
    }

@router.get("/unanswered-analytics")
def unanswered_analytics():

    db = SessionLocal()

    try:

        total_questions = (
            db.query(UnansweredQuestion)
            .count()
        )

        pending_questions = (
            db.query(UnansweredQuestion)
            .filter(
                UnansweredQuestion.status == "Pending"
            )
            .count()
        )

        resolved_questions = (
            db.query(UnansweredQuestion)
            .filter(
                UnansweredQuestion.status == "Resolved"
            )
            .count()
        )

        if total_questions == 0:
            resolution_percentage = 0
        else:
            resolution_percentage = round(
                (resolved_questions / total_questions) * 100,
                2
            )

        knowledge_documents = (
            db.query(Document)
            .count()
        )

        recently_resolved = (
            db.query(UnansweredQuestion)
            .filter(
                UnansweredQuestion.status == "Resolved"
            )
            .order_by(
                UnansweredQuestion.resolved_at.desc()
            )
            .all()
        )
        recently_resolved_data = []

        for question in recently_resolved:

            recently_resolved_data.append(
                {
                    "question": question.question,
                    "resolved_document": question.resolved_document,
                    "resolved_at": question.resolved_at
                }
            )

        return {
            "total_questions": total_questions,
            "pending_questions": pending_questions,
            "resolved_questions": resolved_questions,
            "resolution_percentage": resolution_percentage,
            "knowledge_documents": knowledge_documents,
            "recently_resolved": recently_resolved_data
        }

    finally:

        db.close()


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

from fastapi import Depends, Query
from sqlalchemy.orm import Session
from database.postgres import get_db
from database.models import Document

@router.get("/recent-uploads")
def get_recent_uploads(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db)
):

    total = db.query(Document).count()

    documents = (
        db.query(Document)
        .order_by(Document.uploaded_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    uploads = []

    for doc in documents:
        uploads.append({
            "document_id": doc.id,
            "document_name": doc.document_name,
            "workflow": doc.workflow,
            "page_name": doc.page_name,
            "uploaded_at": doc.uploaded_at.strftime("%d %b %Y %H:%M"),
            "status": "Indexed"
        })

    return {
        "items": uploads,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }

from fastapi import Query
from sqlalchemy import func


@router.get("/most-frequent-questions")
def get_most_frequent_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50)
):

    db = SessionLocal()

    try:
        total = (
            db.query(
                func.lower(func.trim(UserFeedback.question))
            )
            .group_by(
                func.lower(func.trim(UserFeedback.question))
            )
            .having(
                func.count(UserFeedback.id) >= 2
            )
            .count()
        )

        questions = (
            db.query(
                func.lower(
                    func.trim(UserFeedback.question)
                ).label("question"),
                func.count(
                    UserFeedback.id
                ).label("count")
            )
            .group_by(
                func.lower(
                    func.trim(UserFeedback.question)
                )
            )
            .having(
                func.count(UserFeedback.id) >= 2
            )
            .order_by(
                func.count(UserFeedback.id).desc()
            )
            .offset(
                (page - 1) * page_size
            )
            .limit(page_size)
            .all()
        )

        return {
            "items": [
                {
                    "question": question.capitalize(),
                    "count": count
                }
                for question, count in questions
            ],
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (
                (total + page_size - 1)
                // page_size
            )
        }

    finally:

        db.close()