from datetime import datetime

from database.models import UnansweredQuestion
from database.postgres import SessionLocal
from services.question_resolution_service import QuestionResolutionService
from services.retrieval_manager import retrieve


class UnansweredResolutionService:

    def resolve_after_document_upload(
        self,
        document_name: str,
        audience: str
    ):

        db = SessionLocal()

        unanswered_questions = (
            db.query(UnansweredQuestion)
            .filter(
                UnansweredQuestion.status == "Pending",
                UnansweredQuestion.audience == audience
            )
            .all()
        )

        print(
            f"Found {len(unanswered_questions)} pending unanswered questions."
        )

        db.close()

        resolution_checker = QuestionResolutionService()
        resolved_questions = []

        RELEVANCE_THRESHOLD = 0.40

        for unanswered in unanswered_questions:

            print(f"\nChecking: {unanswered.question}")

            try:

                retrieval_result = retrieve(
                    unanswered.question,
                    unanswered.audience
                )

                context = retrieval_result["context"]
                score = retrieval_result["score"]
                chunks = retrieval_result["chunks"]

                if score >= RELEVANCE_THRESHOLD:

                    print("Passed Relevance Threshold")

                    is_resolved = resolution_checker.is_question_resolved(
                        question=unanswered.question,
                        context=context
                    )

                    if is_resolved:

                        print("Gemini: YES")

                        db = SessionLocal()

                        try:

                            db_question = (
                                db.query(UnansweredQuestion)
                                .filter(
                                    UnansweredQuestion.id == unanswered.id
                                )
                                .first()
                            )

                            if db_question:

                                db_question.status = "Resolved"
                                db_question.resolved_document = document_name
                                db_question.resolved_at = datetime.utcnow()

                                db.commit()

                        finally:

                            db.close()

                        resolved_questions.append(
                            {
                                "question": unanswered.question,
                                "document": document_name,
                                "score": score
                            }
                        )

                    else:

                        print("Gemini: NO")

                else:

                    print("Below Relevance Threshold")

            except Exception as e:

                print(f"Retrieval Failed: {e}")

        return resolved_questions