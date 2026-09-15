from fastapi import APIRouter, Query

from database.mongo_helpers import (
    get_documents_collection,
    get_unanswered_questions_collection,
    get_user_feedback_collection
)

from services.chatbot_settings_service import (
    get_chatbot_status,
    set_chatbot_status
)


router = APIRouter()


# --------------------------------------------------
# Chatbot Status
# --------------------------------------------------

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


# --------------------------------------------------
# Unanswered Question Analytics
# --------------------------------------------------

@router.get("/unanswered-analytics")
def unanswered_analytics():

    collection = get_unanswered_questions_collection()
    documents_collection = get_documents_collection()

    total_questions = collection.count_documents({})

    pending_questions = collection.count_documents({
        "status": "Pending"
    })

    resolved_questions = collection.count_documents({
        "status": "Resolved"
    })

    if total_questions == 0:
        resolution_percentage = 0
    else:
        resolution_percentage = round(
            (resolved_questions / total_questions) * 100,
            2
        )

    knowledge_documents = documents_collection.count_documents({})

    recently_resolved = (
        collection
        .find({
            "status": "Resolved"
        })
        .sort(
            "resolved_at",
            -1
        )
        .limit(10)
    )

    recently_resolved_data = []

    for question in recently_resolved:

        recently_resolved_data.append({
            "question": question.get("question"),
            "resolved_document": question.get(
                "resolved_document"
            ),
            "resolved_at": question.get(
                "resolved_at"
            )
        })

    return {
        "total_questions": total_questions,
        "pending_questions": pending_questions,
        "resolved_questions": resolved_questions,
        "resolution_percentage": resolution_percentage,
        "knowledge_documents": knowledge_documents,
        "recently_resolved": recently_resolved_data
    }


# --------------------------------------------------
# Knowledge Gaps
# --------------------------------------------------

@router.get("/knowledge-gaps")
def get_knowledge_gaps():

    collection = get_unanswered_questions_collection()

    questions = (
        collection
        .find({})
        .sort(
            "created_at",
            -1
        )
    )

    return [
        {
            "id": str(q["_id"]),
            "question": q.get("question"),
            "audience": q.get("audience"),
            "page_name": q.get("page_name"),
            "source_document": q.get(
                "source_document"
            ),
            "created_at": q.get("created_at")
        }
        for q in questions
    ]


# --------------------------------------------------
# Recent Uploads
# --------------------------------------------------

@router.get("/recent-uploads")
def get_recent_uploads(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50)
):

    collection = get_documents_collection()

    total = collection.count_documents({})

    documents = (
        collection
        .find({})
        .sort(
            "uploaded_at",
            -1
        )
        .skip(
            (page - 1) * page_size
        )
        .limit(
            page_size
        )
    )

    uploads = []

    for doc in documents:

        uploaded_at = doc.get(
            "uploaded_at"
        )

        uploads.append({
            "document_id": str(
                doc["_id"]
            ),
            "document_name": doc.get(
                "document_name"
            ),
            "workflow": doc.get(
                "workflow"
            ),
            "page_name": doc.get(
                "page_name"
            ),
            "audience": doc.get(
                "audience"
            ),
            "uploaded_at": (
                uploaded_at.strftime(
                    "%d %b %Y %H:%M"
                )
                if uploaded_at
                else None
            ),
            "status": "Indexed"
        })

    return {
        "items": uploads,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (
            (total + page_size - 1)
            // page_size
        )
    }


# --------------------------------------------------
# Most Frequent Questions
# --------------------------------------------------

@router.get("/most-frequent-questions")
def get_most_frequent_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50)
):

    collection = get_user_feedback_collection()

    pipeline = [

        {
            "$project": {
                "question": {
                    "$toLower": {
                        "$trim": {
                            "input": "$question"
                        }
                    }
                }
            }
        },

        {
            "$group": {
                "_id": "$question",
                "count": {
                    "$sum": 1
                }
            }
        },

        {
            "$match": {
                "count": {
                    "$gte": 2
                }
            }
        },

        {
            "$sort": {
                "count": -1
            }
        }
    ]

    grouped_questions = list(
        collection.aggregate(
            pipeline
        )
    )

    total = len(
        grouped_questions
    )

    start = (
        (page - 1)
        * page_size
    )

    end = start + page_size

    questions = grouped_questions[
        start:end
    ]

    return {
        "items": [
            {
                "question": item["_id"].capitalize(),
                "count": item["count"]
            }
            for item in questions
        ],

        "page": page,

        "page_size": page_size,

        "total": total,

        "total_pages": (
            (total + page_size - 1)
            // page_size
        )
    }