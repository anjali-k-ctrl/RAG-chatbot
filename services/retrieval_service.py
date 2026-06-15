from services.s3_service import download_document_from_s3
from services.document_loader import extract_docx_text
from database.postgres import SessionLocal
from database.models import Document
import re


def retrieve_documents(query: str, page_name: str = None):

    db = SessionLocal()

    try:

        documents = db.query(Document).all()

        latest_docs = {}

        for doc in documents:

            page = doc.page_name

            if (
                page not in latest_docs
                or
                doc.uploaded_at >
                latest_docs[page].uploaded_at
            ):
                latest_docs[page] = doc

        documents = list(
            latest_docs.values()
        )

        print("\nLATEST DOCUMENTS:")
        for doc in documents:
            print(doc.page_name, doc.document_name)

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

            try:
                temp_file = download_document_from_s3(
                    doc.s3_key
                )

                document_text = extract_docx_text(
                    temp_file
                )

                content = document_text.lower()

            except Exception as e:

                print(
                    f"Failed to load {doc.document_name}: {e}"
                )

                continue

            for word in keywords:

                if word in doc.page_name.lower():
                    score += 20

                if word in doc.document_name.lower():
                    score += 10

                score += content.count(word)

            if score > 0:
                matches.append((score, doc))

        matches.sort(
            key=lambda x: (
                x[0],
                x[1].uploaded_at
            ),
            reverse=True
        )

        return [doc for score, doc in matches[:3]]

    finally:
        db.close()