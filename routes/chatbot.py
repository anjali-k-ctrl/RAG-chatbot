from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.retrieval_manager import retrieve
from services.outage_service import log_opensearch_outage
from services.failed_retrieval_service import save_failed_request
from services.gemini_service import generate_answer
from services.feedback_service import save_unanswered_question
from services.logging_service import log_retrieval
from services.irrelevant_question_service import (
    save_irrelevant_question
)
from services.chatbot_settings_service import (
    get_chatbot_status
)

from database.mongo_helpers import (
    get_user_feedback_collection
)


RELEVANCE_THRESHOLD = 0.45

router = APIRouter()


# --------------------------------------------------
# Chat Request
# --------------------------------------------------

class ChatRequest(BaseModel):

    message: str

    page_name: str | None = None

    audience: str


# --------------------------------------------------
# Chat
# --------------------------------------------------

@router.post("/chat")
def chat(request: ChatRequest):

    print("CHAT ENDPOINT HIT")

    if not get_chatbot_status():

        raise HTTPException(
            status_code=503,
            detail="Chatbot is currently unavailable."
        )

    try:

        retrieval = retrieve(
            request.message,
            request.audience
        )

        context = retrieval["context"]
        top_score = retrieval["score"]
        chunks = retrieval["chunks"]

        print("\n===== RETRIEVED CHUNKS =====")

        for chunk in chunks:

            print(
                f"{chunk['document_name']} | "
                f"Score={chunk['score']}"
            )

    except Exception as e:

        print(
            f"Retrieval Error: {e}"
        )

        save_failed_request(
            question=request.message,
            page_name=request.page_name,
            error=str(e),
            service="OpenSearch"
        )

        return {
            "answer": (
                "I'm currently unable to access the "
                "MediaShipper documentation because the "
                "search service is temporarily unavailable.\n\n"
                "Your question has been recorded for review. "
                "Please try again in a few minutes."
            )
        }

    print("\n===== QUESTION =====")
    print(request.message)

    print("\n===== TOP SCORE =====")
    print(top_score)

    # --------------------------------------------------
    # No Context Found
    # --------------------------------------------------

    if not context.strip():

        save_unanswered_question(
            question=request.message,
            audience=request.audience,
            page_name=request.page_name,
            source_document=None
        )

        return {
            "answer": (
                "I'm only able to help with MediaShippers-related "
                "questions — like deals, rights, payments, content "
                "submissions, and buyer/seller rules. Please ask "
                "me something about the MediaShippers platform!"
            )
        }

    print("\n===== CONTEXT SENT TO GEMINI =====")
    print(context[:1000])

    # --------------------------------------------------
    # Generate Answer
    # --------------------------------------------------

    result = generate_answer(
        question=request.message,
        chunks=chunks
    )

    answer = result["answer"]
    followups = result["followups"]
    source_document = result["source_document"]

    retrieved_documents = {
        chunk["document_name"]
        for chunk in chunks
    }

    if source_document not in retrieved_documents:

        print(
            "Gemini returned an invalid source document."
        )

        source_document = None

    print("\n===== SOURCE =====")
    print(source_document)

    # --------------------------------------------------
    # Determine Answer / Relevance
    # --------------------------------------------------

    answered = "YES"

    if (
        "I'm only able to help with MediaShippers-related "
        "questions — like deals, rights, payments, content "
        "submissions, and buyer/seller rules. Please ask "
        "me something about the MediaShippers platform!"
        in answer
    ):

        answered = "NO"

    relevant = "YES"

    if top_score < RELEVANCE_THRESHOLD:

        relevant = "NO"

        save_irrelevant_question(
            question=request.message,
            reason=(
                f"Similarity score {top_score:.2f} "
                f"below threshold "
                f"{RELEVANCE_THRESHOLD}"
            )
        )

    # --------------------------------------------------
    # Retrieval Logging
    # --------------------------------------------------

    log_retrieval(
        request.message,
        top_score,
        relevant,
        answered
    )

    # --------------------------------------------------
    # Save Relevant Unanswered Question
    # --------------------------------------------------

    if (
        "I'm only able to help with MediaShippers-related "
        "questions — like deals, rights, payments, content "
        "submissions, and buyer/seller rules. Please ask "
        "me something about the MediaShippers platform!"
        in answer
    ):

        if top_score >= RELEVANCE_THRESHOLD:

            print(
                "RELEVANT UNANSWERED QUESTION SAVED"
            )

            save_unanswered_question(
                question=request.message,
                audience=request.audience,
                page_name=request.page_name,
                source_document=source_document
            )

        else:

            print(
                f"IGNORED IRRELEVANT QUESTION "
                f"(score={top_score})"
            )

    print("\n===== GEMINI RESPONSE =====")
    print(answer)

    return {
        "answer": answer,
        "followups": followups,
        "sources": (
            [source_document]
            if source_document
            else []
        )
    }


# --------------------------------------------------
# Recent Feedback
# --------------------------------------------------

@router.get("/recent-feedback")
def recent_feedback():

    collection = get_user_feedback_collection()

    feedback = (
        collection
        .find({})
        .sort(
            "created_at",
            -1
        )
        .limit(20)
    )

    result = []

    for f in feedback:

        created_at = f.get(
            "created_at"
        )

        result.append({
            "question": f.get(
                "question"
            ),
            "helpful": f.get(
                "helpful"
            ),
            "category": f.get(
                "feedback_category"
            ),
            "feedback": f.get(
                "feedback"
            ),
            "created_at": (
                created_at.strftime(
                    "%Y-%m-%d %H:%M"
                )
                if created_at
                else None
            )
        })

    return result