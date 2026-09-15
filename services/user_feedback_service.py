from datetime import datetime, UTC

from database.mongo_helpers import get_user_feedback_collection


def save_user_feedback(
    question: str,
    chatbot_answer: str,
    helpful: bool,
    page_name: str = None,
    feedback_category: str = None,
    feedback: str = None
):
    collection = get_user_feedback_collection()

    record = {
        "question": question,
        "chatbot_answer": chatbot_answer,
        "helpful": helpful,
        "page_name": page_name,
        "feedback_category": feedback_category,
        "feedback": feedback,
        "reviewed": False,
        "reviewed_at": None,
        "created_at": datetime.now(UTC)
    }

    collection.insert_one(record)