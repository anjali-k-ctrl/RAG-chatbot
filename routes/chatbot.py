from fastapi import APIRouter
from pydantic import BaseModel

from services.vector_retrieval_service import (
    retrieve_context
)
from services.gemini_service import generate_answer

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    page_name: str | None = None


@router.post("/chat")
def chat(request: ChatRequest):

    print("CHAT ENDPOINT HIT")

    context = retrieve_context(
        request.message
    )

    print("\n===== RETRIEVED CONTEXT =====")
    print(context[:500])

    if not context.strip():

        return {
            "answer":
            "I could not find this information in the MediaShipper documentation."
        }

    answer = generate_answer(
        request.message,
        context
    )

    print("\n===== GEMINI RESPONSE =====")
    print(answer)

    return {
        "answer": answer,
        "sources": [
            "website_documentation_-_sellers__buyers.pdf"
        ]
    }