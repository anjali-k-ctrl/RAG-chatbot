from database.mongo_models import (
    documents_collection,
    unanswered_questions_collection,
    user_feedback_collection,
    system_health_logs_collection,
    failed_retrieval_requests_collection,
    irrelevant_questions_collection,
    chatbot_settings_collection,
)


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