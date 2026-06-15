from services.feedback_service import save_unanswered_question
from fastapi import APIRouter
from pydantic import BaseModel

from services.retrieval_service import retrieve_documents
from services.gemini_service import generate_answer

from services.s3_service import download_document_from_s3
from services.document_loader import extract_docx_text

router = APIRouter()
class ChatRequest(BaseModel):
    message: str
    page_name: str | None = None

@router.post("/chat")
def chat(request: ChatRequest):

    print("CHAT ENDPOINT HIT")

    documents = retrieve_documents(
        query=request.message,
        page_name=request.page_name
    )

    print("DOCUMENTS FOUND:", len(documents))

    if not documents:

        print("SAVING UNANSWERED QUESTION - NO DOCUMENTS FOUND")

        save_unanswered_question(
            question=request.message,
            page_name=request.page_name,
            source_document=None
        )

        return {
            "answer":
            "I could not find this information in the MediaShipper documentation."
        }

    contexts = []

    for doc in documents:

        try:

            temp_file = download_document_from_s3(
                doc.s3_key
            )

            text = extract_docx_text(
                temp_file
            )

            contexts.append(text)

        except Exception as e:

            print(
                f"Failed to load {doc.document_name}: {e}"
            )

    context = "\n\n".join(contexts)


    answer = generate_answer(
        request.message,
        context
    )

    print("\n===== GEMINI RESPONSE =====")
    print(answer)

    if "I could not find this information" in answer:

        print("SAVING UNANSWERED QUESTION")

        save_unanswered_question(
            question=request.message,
            page_name=request.page_name,
            source_document=documents[0].document_name
        )

    return {
        "answer": answer,
        "sources": [documents[0].document_name]
    }