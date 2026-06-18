from fastapi import APIRouter
from pydantic import BaseModel

from services.vector_retrieval_service import (
    retrieve_context
)
from services.gemini_service import generate_answer
from services.feedback_service import (
    save_unanswered_question
)

from services.logging_service import (
    log_retrieval
)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    page_name: str | None = None


@router.post("/chat")
def chat(request: ChatRequest):

    print("CHAT ENDPOINT HIT")

    context, top_score = retrieve_context(
        request.message
    )

    print("\n===== QUESTION =====")
    print(request.message)

    print("\n===== TOP SCORE =====")
    print(top_score)

    print("\n===== SOURCE =====")
    print("website_documentation_-_sellers__buyers.pdf")

    log_retrieval(
        request.message,
        top_score
    )

    if not context.strip():

        save_unanswered_question(
            question=request.message,
            page_name=request.page_name,
            source_document=None
        )

        return {
            "answer":
            "I could not find this information in the MediaShipper documentation."
        }

    print("\n===== CONTEXT SENT TO GEMINI =====")
    print(context[:1000])

    answer = generate_answer(
        request.message,
        context
    )

    if (
        "I could not find this information"
        in answer
    ):

        print("UNANSWERED QUESTION SAVED")

        save_unanswered_question(
            question=request.message,
            page_name=request.page_name,
            source_document="website_documentation_-_sellers__buyers.pdf"
        )

    print("\n===== GEMINI RESPONSE =====")
    print(answer)

    return {
        "answer": answer,
        "sources": [
            "website_documentation_-_sellers__buyers.pdf"
        ]
    }