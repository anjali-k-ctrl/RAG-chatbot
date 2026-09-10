from database.postgres import SessionLocal
from database.models import UnansweredQuestion


def resolve_pending_questions(uploaded_document):

    db = SessionLocal()

    try:

        pending_questions = (
            db.query(UnansweredQuestion)
            .filter(UnansweredQuestion.status == "Pending")
            .all()
        )

        return {
            "pending_before": len(pending_questions),
            "resolved_now": 0,
            "pending_after": len(pending_questions)
        }

    finally:
        db.close()