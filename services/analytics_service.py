import csv

from collections import defaultdict
from datetime import datetime, timedelta

from database.mongo_helpers import (
    get_unanswered_questions_collection
)


# --------------------------------------------------
# General Analytics
# --------------------------------------------------

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


# --------------------------------------------------
# Top Unanswered Questions
# --------------------------------------------------

def get_top_unanswered_questions():

    collection = get_unanswered_questions_collection()

    questions = (
        collection
        .find({
            "status": "Pending"
        })
        .sort(
            "count",
            -1
        )
        .limit(10)
    )

    return [
        {
            "question": q.get("question"),
            "count": q.get("count", 0),
            "page_name": q.get("page_name")
        }
        for q in questions
    ]


# --------------------------------------------------
# Recent Unanswered Questions
# --------------------------------------------------

def get_recent_unanswered_questions():

    collection = get_unanswered_questions_collection()

    questions = (
        collection
        .find({})
        .sort(
            "created_at",
            -1
        )
        .limit(10)
    )

    result = []

    for q in questions:

        resolved_at = q.get(
            "resolved_at"
        )

        created_at = q.get(
            "created_at"
        )

        result.append({
            "question": q.get("question"),

            "count": q.get(
                "count",
                0
            ),

            "status": q.get(
                "status"
            ),

            "source_document": q.get(
                "source_document"
            ),

            "resolved_document": q.get(
                "resolved_document"
            ),

            "resolved_at": (
                resolved_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if resolved_at
                else None
            ),

            "created_at": (
                created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if created_at
                else None
            )
        })

    return result


# --------------------------------------------------
# Daily Report
# --------------------------------------------------

def get_daily_report(
    from_date=None,
    to_date=None
):

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

            record_date = datetime.fromisoformat(
                row["timestamp"]
            )

            if from_date:

                if (
                    record_date.date()
                    < datetime.strptime(
                        from_date,
                        "%Y-%m-%d"
                    ).date()
                ):
                    continue

            if to_date:

                if (
                    record_date.date()
                    > datetime.strptime(
                        to_date,
                        "%Y-%m-%d"
                    ).date()
                ):
                    continue

            label = record_date.strftime(
                "%d %b"
            )

            daily[label]["questions"] += 1

            if row["answered"] == "YES":

                daily[label]["answered"] += 1

            else:

                daily[label]["unanswered"] += 1

    report = []

    for record_date, values in daily.items():

        report.append({
            "date": record_date,
            "questions": values["questions"],
            "answered": values["answered"],
            "unanswered": values["unanswered"]
        })

    return report


# --------------------------------------------------
# Weekly Report
# --------------------------------------------------

def get_weekly_report(
    from_date=None,
    to_date=None
):

    weekly = defaultdict(
        lambda: {
            "questions": 0,
            "answered": 0,
            "unanswered": 0
        }
    )

    from_dt = (
        datetime.strptime(
            from_date,
            "%Y-%m-%d"
        ).date()
        if from_date
        else None
    )

    to_dt = (
        datetime.strptime(
            to_date,
            "%Y-%m-%d"
        ).date()
        if to_date
        else None
    )

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

            record_date = datetime.fromisoformat(
                row["timestamp"]
            ).date()

            # Date filtering
            if from_dt and record_date < from_dt:
                continue

            if to_dt and record_date > to_dt:
                continue

            start = (
                record_date
                - timedelta(
                    days=record_date.weekday()
                )
            )

            end = start + timedelta(
                days=6
            )

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