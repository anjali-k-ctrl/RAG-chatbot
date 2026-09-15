from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import csv
import os

from database.mongo_helpers import (
    get_documents_collection,
    get_unanswered_questions_collection
)

from routes.chatbot import router as chatbot_router
from routes.admin import router as admin_router
from routes.analytics import router as analytics_router
from routes.health import router as health_router
from routes.feedback import router as feedback_router
from routes.upload import router as upload_router


app = FastAPI()


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv(
            "FRONTEND_URL",
            "http://localhost:5500"
        )
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

# Chatbot routes
app.include_router(chatbot_router)

# Admin routes
app.include_router(
    admin_router,
    prefix="/admin"
)

# Analytics routes
app.include_router(
    analytics_router
)

# Health routes
app.include_router(
    health_router
)

# Feedback routes
app.include_router(
    feedback_router
)

# Upload routes
app.include_router(
    upload_router
)


# ============================================================
# DOCUMENT COUNT
# ============================================================

@app.get("/count")
def count_docs():

    collection = get_documents_collection()

    count = collection.count_documents({})

    return {
        "documents": count
    }


# ============================================================
# KNOWLEDGE GAP SUMMARY
# ============================================================

@app.get("/knowledge-gap-summary")
def knowledge_gap_summary():

    collection = get_unanswered_questions_collection()

    questions = list(
        collection.find(
            {},
            {
                "_id": 0,
                "question": 1,
                "page_name": 1,
                "count": 1
            }
        ).sort(
            "count",
            -1
        )
    )

    return questions


# ============================================================
# KNOWLEDGE GAP BY PAGE
# ============================================================

@app.get("/knowledge-gap-by-page")
def knowledge_gap_by_page():

    collection = get_unanswered_questions_collection()

    questions = collection.find(
        {},
        {
            "_id": 0,
            "page_name": 1,
            "count": 1
        }
    )

    summary = {}

    for question in questions:

        page = (
            question.get("page_name")
            or "unknown"
        )

        summary[page] = (
            summary.get(page, 0)
            + question.get("count", 0)
        )

    return summary


# ============================================================
# EXPORT KNOWLEDGE GAPS
# ============================================================

@app.get("/export-knowledge-gaps")
def export_knowledge_gaps():

    collection = get_unanswered_questions_collection()

    questions = list(
        collection.find(
            {}
        ).sort(
            "count",
            -1
        )
    )

    filename = "knowledge_gaps.csv"

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "Question",
            "Workflow Step",
            "Count",
            "Created At"
        ])

        for question in questions:

            created_at = question.get(
                "created_at"
            )

            if created_at:
                created_at = created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            else:
                created_at = ""

            writer.writerow([
                question.get("question"),
                question.get("page_name"),
                question.get("count", 0),
                created_at
            ])

    return FileResponse(
        filename,
        media_type="text/csv",
        filename=filename
    )