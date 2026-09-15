from database.mongodb import db


documents_collection = db["documents"]

unanswered_questions_collection = db["unanswered_questions"]

user_feedback_collection = db["user_feedback"]

system_health_logs_collection = db["system_health_logs"]

failed_retrieval_requests_collection = db["failed_retrieval_requests"]

irrelevant_questions_collection = db["irrelevant_questions"]

chatbot_settings_collection = db["chatbot_settings"]