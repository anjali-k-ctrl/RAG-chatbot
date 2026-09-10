from fastapi import APIRouter
from pydantic import BaseModel

from services.user_feedback_service import (
    save_user_feedback
)

router = APIRouter()


class FeedbackRequest(BaseModel):

    question: str
    chatbot_answer: str
    helpful: bool
    page_name: str | None = None
    feedback_category: str | None = None
    feedback: str | None = None


@router.post("/feedback")
def submit_feedback(request: FeedbackRequest):

    save_user_feedback(
        question=request.question,
        chatbot_answer=request.chatbot_answer,
        helpful=request.helpful,
        page_name=request.page_name,
        feedback_category=request.feedback_category,
        feedback=request.feedback
    )

    return {
        "message": "Feedback saved successfully"
    }