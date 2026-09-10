from database.postgres import SessionLocal
from database.models import IrrelevantQuestion


def save_irrelevant_question(
    question: str,
    reason: str = "Outside MediaShipper documentation scope"
):

    db = SessionLocal()

    try:

        record = IrrelevantQuestion(
            question=question,
            reason=reason
        )

        db.add(record)
        db.commit()

    finally:

        db.close()