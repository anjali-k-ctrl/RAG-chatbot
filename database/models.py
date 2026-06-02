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

    content = Column(Text, nullable=True)

    uploaded_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )