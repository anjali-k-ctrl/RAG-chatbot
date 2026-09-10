from database.postgres import SessionLocal
from database.models import UserFeedback


def save_user_feedback( question: str, chatbot_answer: str, helpful: bool, page_name: str = None, feedback_category: str = None, feedback: str = None ):
    db = SessionLocal()
    try:
        record = UserFeedback( question=question, chatbot_answer=chatbot_answer, helpful=helpful, page_name=page_name, feedback_category=feedback_category, feedback=feedback )
        db.add(record)
        db.commit()
    finally:
        db.close()