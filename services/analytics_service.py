import csv
from collections import defaultdict
from datetime import datetime, timedelta, date

def get_analytics():

    total_questions = 0

    relevant_questions = 0
    irrelevant_questions = 0

    answered_relevant_questions = 0
    unanswered_relevant_questions = 0

    scores = []

    with open(
        "logs/retrieval_logs.csv",
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            total_questions += 1

            scores.append(
                float(row["score"])
            )

            relevant = row.get("relevant")
            answered = row.get("answered")

            if relevant == "YES":

                relevant_questions += 1

                if answered == "YES":

                    answered_relevant_questions += 1

                elif answered == "NO":

                    unanswered_relevant_questions += 1

            elif relevant == "NO":

                irrelevant_questions += 1

    average_score = (
        sum(scores) / len(scores)
        if scores
        else 0
    )

    answer_rate = (
        answered_relevant_questions
        / relevant_questions
        * 100
        if relevant_questions
        else 0
    )

    return {
        "total_questions": total_questions,

        "relevant_questions": relevant_questions,

        "irrelevant_questions": irrelevant_questions,

        "answered_relevant_questions":
            answered_relevant_questions,

        "unanswered_relevant_questions":
            unanswered_relevant_questions,

        "average_score": round(
            average_score,
            2
        ),

        "answer_rate": round(
            answer_rate,
            2
        )
    }

from database.postgres import SessionLocal
from database.models import UnansweredQuestion


def get_top_unanswered_questions():

    db = SessionLocal()

    try:

        questions = (
            db.query(UnansweredQuestion)
            .filter(
                UnansweredQuestion.status == "Pending"
            )
            .order_by(
                UnansweredQuestion.count.desc()
            )
            .limit(10)
            .all()
        )

        return [
            {
                "question": q.question,
                "count": q.count,
                "page_name": q.page_name
            }
            for q in questions
        ]

    finally:
        db.close()

def get_recent_unanswered_questions():

    db = SessionLocal()

    try:

        questions = (
            db.query(UnansweredQuestion)
            .order_by(
                UnansweredQuestion.created_at.desc()
            )
            .limit(10)
            .all()
        )

        return [
            {
                "question": q.question,
                "count": q.count,
                "status": q.status,
                "source_document": q.source_document,
                "resolved_document": q.resolved_document,
                "resolved_at": (
                    q.resolved_at.strftime("%Y-%m-%d %H:%M:%S")
                    if q.resolved_at
                    else None
                ),
                "created_at": q.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
            for q in questions
        ]

    finally:
        db.close()

def get_daily_report( from_date=None, to_date=None):

    daily = defaultdict(
        lambda: {
            "questions": 0,
            "answered": 0,
            "unanswered": 0
        }
    )

    with open(
        "logs/retrieval_logs.csv",
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            date = datetime.fromisoformat(
                row["timestamp"]
            )

            if from_date:

                if date.date() < datetime.strptime(
                    from_date,
                    "%Y-%m-%d"
                ).date():
                    continue

            if to_date:

                if date.date() > datetime.strptime(
                    to_date,
                    "%Y-%m-%d"
                ).date():
                    continue

            label = date.strftime("%d %b")

            daily[label]["questions"] += 1

            if row["answered"] == "YES":

                daily[label]["answered"] += 1

            else:

                daily[label]["unanswered"] += 1

    report = []

    for date, values in daily.items():

        report.append({
            "date": date,
            "questions": values["questions"],
            "answered": values["answered"],
            "unanswered": values["unanswered"]
        })

    return report


from collections import defaultdict
from datetime import datetime, timedelta
import csv


def get_weekly_report(from_date=None, to_date=None):
    print("FROM =", from_date)
    print("TO =", to_date)

    weekly = defaultdict(
        lambda: {
            "questions": 0,
            "answered": 0,
            "unanswered": 0
        }
    )

    from_dt = (
        datetime.strptime(from_date, "%Y-%m-%d").date()
        if from_date else None
    )

    to_dt = (
        datetime.strptime(to_date, "%Y-%m-%d").date()
        if to_date else None
    )
    print("FROM_DT =", from_dt)
    print("TO_DT =", to_dt)

    with open(
        "logs/retrieval_logs.csv",
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            # Ignore irrelevant questions
            if row["relevant"] != "YES":
                continue

            date = datetime.fromisoformat(
                row["timestamp"]
            ).date()

            # Date filtering
            if from_dt and date < from_dt:
                continue

            if to_dt and date > to_dt:
                continue

            start = date - timedelta(days=date.weekday())
            end = start + timedelta(days=6)

            print("Checking:", date)

            if from_dt and date < from_dt:
                print("Skipped because before from_date")
                continue

            if to_dt and date > to_dt:
                print("Skipped because after to_date")
                continue

            print("Included:", date)

            label = (
                f"{start.strftime('%d %b')} - "
                f"{end.strftime('%d %b')}"
            )

            weekly[label]["questions"] += 1

            if row["answered"] == "YES":
                weekly[label]["answered"] += 1
            else:
                weekly[label]["unanswered"] += 1

    report = []

    for week, values in weekly.items():

        report.append({
            "week": week,
            "questions": values["questions"],
            "answered": values["answered"],
            "unanswered": values["unanswered"]
        })

    return report