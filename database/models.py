from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime, UTC

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String, nullable=False)
    workflow = Column(String, nullable=False)
    page_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    s3_key = Column(Text, nullable=True)
    uploaded_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )


class UnansweredQuestion(Base):
    __tablename__ = "unanswered_questions"

    id = Column(Integer, primary_key=True, index=True)

    question = Column(Text, nullable=False)

    page_name = Column(String, nullable=True)

    source_document = Column(String, nullable=True)

    count = Column(Integer, default=1)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )