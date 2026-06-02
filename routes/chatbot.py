from fastapi import APIRouter
from pydantic import BaseModel

from services.retrieval_service import retrieve_documents
from services.gemini_service import generate_answer

router = APIRouter()
class ChatRequest(BaseModel):
    message: str
    page_name: str | None = None

@router.post("/chat")
def chat(request: ChatRequest):

    documents = retrieve_documents(
        query=request.message,
        page_name=request.page_name
    )

    if not documents:
        return {
            "answer":
            "I could not find this information in the MediaShipper documentation."
        }

    context = "\n\n".join(
        doc.content or ""
        for doc in documents
    )

    answer = generate_answer(
        request.message,
        context
    )

    return {
        "answer": answer,
        "sources": [documents[0].document_name]
    }