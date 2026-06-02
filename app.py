from fastapi import FastAPI
from routes.chatbot import router
app = FastAPI()
from database.postgres import SessionLocal
from database.models import Document
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.get("/count")
def count_docs():
    db = SessionLocal()

    count = db.query(Document).count()

    return {
        "documents": count
    }

app.include_router(router)