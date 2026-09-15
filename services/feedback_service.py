import re
from datetime import datetime, UTC

from database.mongo_helpers import get_unanswered_questions_collection


def normalize_question(question: str):
    question = question.lower()

    question = re.sub(
        r'[^\w\s]',
        '',
        question
    )

    return question.strip()


def save_unanswered_question(
    question: str,
    audience: str,
    page_name: str = None,
    source_document: str = None
):
    print("SAVING UNANSWERED QUESTION:", question)

    collection = get_unanswered_questions_collection()

    normalized_question = normalize_question(question)

    collection.update_one(
        {
            "question": normalized_question,
            "audience": audience
        },
        {
            "$inc": {
                "count": 1
            },
            "$setOnInsert": {
                "question": normalized_question,
                "audience": audience,
                "page_name": page_name,
                "source_document": source_document,
                "created_at": datetime.now(UTC),
                "status": "Pending",
                "resolved_at": None,
                "resolved_document": None
            }
        },
        upsert=True
    )