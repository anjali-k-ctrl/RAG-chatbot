from database.mongo_models import deal_proposals_collection
from database.mongo_models import (
    documents_collection,
    unanswered_questions_collection,
    user_feedback_collection,
    system_health_logs_collection,
    failed_retrieval_requests_collection,
    irrelevant_questions_collection,
    chatbot_settings_collection,
    prompt_logs_collection,
)
from datetime import datetime


def get_documents_collection():
    return documents_collection


def get_unanswered_questions_collection():
    return unanswered_questions_collection


def get_user_feedback_collection():
    return user_feedback_collection


def get_system_health_logs_collection():
    return system_health_logs_collection


def get_failed_retrieval_requests_collection():
    return failed_retrieval_requests_collection


def get_irrelevant_questions_collection():
    return irrelevant_questions_collection


def get_chatbot_settings_collection():
    return chatbot_settings_collection

def save_prompt_log(
    question,
    audience,
    page_name=None
):
    result = prompt_logs_collection.insert_one({
        "question": question,
        "audience": audience,
        "page_name": page_name,
        "answered": None,
        "relevant": None,
        "knowledge_gap": None,
        "created_at": datetime.utcnow()
    })

    return result.inserted_id
def update_prompt_log(
    prompt_id,
    relevant,
    answered,
    knowledge_gap,
    score=None
):
    prompt_logs_collection.update_one(
        {"_id": prompt_id},
        {
            "$set": {
                "relevant": relevant,
                "answered": answered,
                "knowledge_gap": knowledge_gap,
                "score": score
            }
        }
    )

def get_deal_proposals_collection():
    return deal_proposals_collection