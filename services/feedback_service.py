import re
from database.postgres import SessionLocal
from database.models import UnansweredQuestion

def normalize_question(
    question: str
):

    question = question.lower()

    question = re.sub(
        r'[^\w\s]',
        '',
        question
    )

    return question.strip()



def save_unanswered_question(
    question: str,
    page_name: str = None,
    source_document: str = None
):
    print("SAVING UNANSWERED QUESTION:", question)

    db = SessionLocal()

    try:

        normalized_question = normalize_question(
            question
        )

        existing = (
            db.query(UnansweredQuestion)
            .filter(
                UnansweredQuestion.question == normalized_question
            )
            .first()
        )

        if existing:

            existing.count += 1

        else:

            entry = UnansweredQuestion(
                question=normalized_question,
                page_name=page_name,
                source_document=source_document,
                count=1
            )

            db.add(entry)

        db.commit()

    finally:
        db.close()