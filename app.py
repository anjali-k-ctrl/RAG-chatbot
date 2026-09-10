from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import csv

from database.postgres import SessionLocal
from database.models import Document, UnansweredQuestion

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
    allow_origins=["*"],
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

    db = SessionLocal()

    try:

        count = (
            db.query(Document)
            .count()
        )

        return {
            "documents": count
        }

    finally:

        db.close()


# ============================================================
# KNOWLEDGE GAP SUMMARY
# ============================================================

@app.get("/knowledge-gap-summary")
def knowledge_gap_summary():

    db = SessionLocal()

    try:

        questions = (
            db.query(UnansweredQuestion)
            .order_by(
                UnansweredQuestion.count.desc()
            )
            .all()
        )

        return [
            {
                "question": q.question,
                "page_name": q.page_name,
                "count": q.count
            }
            for q in questions
        ]

    finally:

        db.close()


# ============================================================
# KNOWLEDGE GAP BY PAGE
# ============================================================

@app.get("/knowledge-gap-by-page")
def knowledge_gap_by_page():

    db = SessionLocal()

    try:

        questions = (
            db.query(UnansweredQuestion)
            .all()
        )

        summary = {}

        for q in questions:

            page = (
                q.page_name
                or "unknown"
            )

            summary[page] = (
                summary.get(page, 0)
                + q.count
            )

        return summary

    finally:

        db.close()


# ============================================================
# EXPORT KNOWLEDGE GAPS
# ============================================================

@app.get("/export-knowledge-gaps")
def export_knowledge_gaps():

    db = SessionLocal()

    try:

        questions = (
            db.query(UnansweredQuestion)
            .order_by(
                UnansweredQuestion.count.desc()
            )
            .all()
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

            for q in questions:

                writer.writerow([
                    q.question,
                    q.page_name,
                    q.count,
                    q.created_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ])

        return FileResponse(
            filename,
            media_type="text/csv",
            filename=filename
        )

    finally:

        db.close()