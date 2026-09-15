from datetime import datetime, UTC
from database.mongo_helpers import (
    get_irrelevant_questions_collection
)
def save_irrelevant_question(
    question: str,
    reason: str = "Outside MediaShipper documentation scope"
):
    collection = get_irrelevant_questions_collection()
    record = {
        "question": question,
        "reason": reason,
        "created_at": datetime.now(UTC)
    }
    collection.insert_one(record)