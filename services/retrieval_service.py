from database.postgres import SessionLocal
from database.models import Document
import re


def retrieve_documents(query: str, page_name: str = None):

    db = SessionLocal()

    try:

        documents = db.query(Document).all()

        if page_name:
            documents = [
                doc
                for doc in documents
                if doc.page_name.lower() == page_name.lower()
            ]
        STOP_WORDS = {
            "how", "do", "i", "the", "is", "are",
            "a", "an", "to", "of", "for", "in",
            "on", "and", "what", "where", "when"
        }

        keywords = [
            word
            for word in re.findall(r"\w+", query.lower())
            if word not in STOP_WORDS
        ]


        matches = []

        for doc in documents:

            score = 0

            content = (doc.content or "").lower()

            for word in keywords:

                if word in doc.page_name.lower():
                    score += 20

                if word in doc.document_name.lower():
                    score += 10

                score += content.count(word)

            if score > 0:
                matches.append((score, doc))

        matches.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [doc for score, doc in matches[:3]]

    finally:
        db.close()