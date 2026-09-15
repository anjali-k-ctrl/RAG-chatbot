from datetime import datetime, UTC

from database.mongo_helpers import (
    get_unanswered_questions_collection
)

from services.question_resolution_service import (
    QuestionResolutionService
)

from services.retrieval_manager import (
    retrieve
)


class UnansweredResolutionService:

    def resolve_after_document_upload(
        self,
        document_name: str,
        audience: str
    ):

        collection = (
            get_unanswered_questions_collection()
        )

        # ----------------------------------------
        # FIND PENDING QUESTIONS
        # FOR THE SAME AUDIENCE
        # ----------------------------------------

        unanswered_questions = list(
            collection.find({
                "status": "Pending",
                "audience": audience
            })
        )

        print(
            f"Found {len(unanswered_questions)} "
            f"pending unanswered questions."
        )

        resolution_checker = (
            QuestionResolutionService()
        )

        resolved_questions = []

        RELEVANCE_THRESHOLD = 0.40

        # ----------------------------------------
        # CHECK EACH QUESTION
        # ----------------------------------------

        for unanswered in unanswered_questions:

            question = unanswered.get(
                "question"
            )

            question_audience = unanswered.get(
                "audience"
            )

            print(
                f"\nChecking: {question}"
            )

            try:

                retrieval_result = retrieve(
                    question,
                    question_audience
                )

                context = retrieval_result[
                    "context"
                ]

                score = retrieval_result[
                    "score"
                ]

                chunks = retrieval_result[
                    "chunks"
                ]

                # ----------------------------------------
                # RELEVANCE CHECK
                # ----------------------------------------

                if score >= RELEVANCE_THRESHOLD:

                    print(
                        "Passed Relevance Threshold"
                    )

                    is_resolved = (
                        resolution_checker
                        .is_question_resolved(
                            question=question,
                            context=context
                        )
                    )

                    # ----------------------------------------
                    # RESOLVE QUESTION
                    # ----------------------------------------

                    if is_resolved:

                        print(
                            "Gemini: YES"
                        )

                        collection.update_one(
                            {
                                "_id": unanswered["_id"]
                            },
                            {
                                "$set": {
                                    "status": "Resolved",
                                    "resolved_document":
                                        document_name,
                                    "resolved_at":
                                        datetime.now(UTC)
                                }
                            }
                        )

                        resolved_questions.append({
                            "question": question,
                            "document": document_name,
                            "score": score
                        })

                    else:

                        print(
                            "Gemini: NO"
                        )

                else:

                    print(
                        "Below Relevance Threshold"
                    )

            except Exception as e:

                print(
                    f"Retrieval Failed: {e}"
                )

        return resolved_questions