from database.mongo_helpers import get_unanswered_questions_collection


def resolve_pending_questions(uploaded_document):
    collection = get_unanswered_questions_collection()

    pending_questions = list(
        collection.find({
            "status": "Pending"
        })
    )

    return {
        "pending_before": len(pending_questions),
        "resolved_now": 0,
        "pending_after": len(pending_questions)
    }