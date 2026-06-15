from database.postgres import SessionLocal
from database.models import UnansweredQuestion


def save_unanswered_question(
    question: str,
    page_name: str = None,
    source_document: str = None
):
    print("SAVING UNANSWERED QUESTION:", question)

    db = SessionLocal()

    try:

        existing = (
            db.query(UnansweredQuestion)
            .filter(
                UnansweredQuestion.question == question,
                UnansweredQuestion.page_name == page_name
            )
            .first()
        )

        if existing:

            existing.count += 1

        else:

            entry = UnansweredQuestion(
                question=question,
                page_name=page_name,
                source_document=source_document,
                count=1
            )

            db.add(entry)

        db.commit()

    finally:
        db.close()