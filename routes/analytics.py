from datetime import datetime, UTC
from bson import ObjectId
from fastapi import APIRouter, Query, HTTPException

from services.analytics_service import (
    get_analytics,
    get_top_unanswered_questions,
    get_recent_unanswered_questions,
    get_daily_report,
    get_weekly_report
)

from database.mongo_helpers import (
    get_user_feedback_collection,
    get_irrelevant_questions_collection
)


router = APIRouter()


# --------------------------------------------------
# General Analytics
# --------------------------------------------------

@router.get("/analytics")
def analytics():

    return get_analytics()


# --------------------------------------------------
# Top Unanswered Questions
# --------------------------------------------------

@router.get("/top-unanswered-questions")
def top_unanswered_questions():

    return get_top_unanswered_questions()


# --------------------------------------------------
# Recent Unanswered Questions
# --------------------------------------------------

@router.get("/recent-unanswered-questions")
def recent_unanswered_questions():

    return get_recent_unanswered_questions()


# --------------------------------------------------
# Daily Report
# --------------------------------------------------

@router.get("/daily-report")
def daily_report(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None)
):

    return get_daily_report(
        from_date,
        to_date
    )


# --------------------------------------------------
# Weekly Report
# --------------------------------------------------

@router.get("/weekly-report")
def weekly_report(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None)
):

    return get_weekly_report(
        from_date,
        to_date
    )


# --------------------------------------------------
# Recent User Feedback
# --------------------------------------------------

@router.get("/recent-user-feedback")
def recent_user_feedback(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50)
):

    collection = get_user_feedback_collection()

    total = collection.count_documents({})

    feedback = (
        collection
        .find({})
        .sort(
            "created_at",
            -1
        )
        .skip(
            (page - 1) * page_size
        )
        .limit(
            page_size
        )
    )

    items = []

    for f in feedback:

        created_at = f.get(
            "created_at"
        )

        items.append({
            "id": str(
                f["_id"]
            ),
            "question": f.get(
                "question"
            ),
            "chatbot_answer": f.get(
                "chatbot_answer"
            ),
            "helpful": f.get(
                "helpful"
            ),
            "category": f.get(
                "feedback_category"
            ),
            "feedback": f.get(
                "feedback"
            ),
            "reviewed": f.get(
                "reviewed"
            ),
            "created_at": (
                created_at.strftime(
                    "%Y-%m-%d %H:%M"
                )
                if created_at
                else None
            )
        })

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (
            (total + page_size - 1)
            // page_size
        )
    }


# --------------------------------------------------
# Mark Feedback as Reviewed
# --------------------------------------------------

@router.post(
    "/feedback/{feedback_id}/review"
)
def mark_feedback_reviewed(
    feedback_id: str
):

    collection = get_user_feedback_collection()

    result = collection.update_one(
        {
            "_id": ObjectId(feedback_id)
        },
        {
            "$set": {
                "reviewed": True,
                "reviewed_at": datetime.now(UTC)
            }
        }
    )

    if result.matched_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Feedback not found"
        )

    return {
        "message": "Feedback marked as reviewed."
    }


# --------------------------------------------------
# Recent Irrelevant Questions
# --------------------------------------------------

@router.get("/recent-irrelevant-questions")
def recent_irrelevant_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50)
):

    collection = (
        get_irrelevant_questions_collection()
    )

    total = collection.count_documents({})

    questions = (
        collection
        .find({})
        .sort(
            "created_at",
            -1
        )
        .skip(
            (page - 1) * page_size
        )
        .limit(
            page_size
        )
    )

    items = []

    for q in questions:

        created_at = q.get(
            "created_at"
        )

        items.append({
            "question": q.get(
                "question"
            ),
            "reason": q.get(
                "reason"
            ),
            "created_at": (
                created_at.strftime(
                    "%Y-%m-%d %H:%M"
                )
                if created_at
                else None
            )
        })

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (
            (total + page_size - 1)
            // page_size
        )
    }