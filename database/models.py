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

    audience = Column(
        String,
        nullable=False,
        index=True
    )


class UnansweredQuestion(Base):
    __tablename__ = "unanswered_questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    audience = Column( String, nullable=False, index=True )
    page_name = Column(String, nullable=True)
    source_document = Column(String, nullable=True)
    count = Column(Integer, default=1)
    created_at = Column( DateTime, default=lambda: datetime.now(UTC) )
    status = Column( String, default="Pending" )
    resolved_at = Column( DateTime, nullable=True)  
    resolved_document = Column( String, nullable=True )

from sqlalchemy import ( Column, Integer, String, Text, DateTime, Boolean, Float)
from sqlalchemy import Boolean

from datetime import datetime

class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    chatbot_answer = Column(Text, nullable=False)
    page_name = Column(String)
    helpful = Column(Boolean, nullable=False)
    feedback_category = Column(String)
    feedback = Column(Text)

    reviewed = Column(Boolean, default=False)
    reviewed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

from datetime import datetime
class SystemHealthLog(Base):
    __tablename__ = "system_health_logs"
    id = Column( Integer, primary_key=True, index=True )
    timestamp = Column( DateTime, default=datetime.utcnow )
    service = Column( String, nullable=False )
    status = Column( String, nullable=False )
    question = Column( Text )
    page_name = Column( String )
    error = Column( Text )
    retry_count = Column( Integer, default=0 )
    circuit_open = Column( Boolean, default=False )
    retrieval_source = Column( String )
    response_time_ms = Column( Float )


from sqlalchemy import Boolean
class FailedRetrievalRequest(Base):

    __tablename__ = "failed_retrieval_requests"
    id = Column( Integer, primary_key=True, index=True )
    question = Column( Text, nullable=False )
    page_name = Column( String )
    error = Column( Text )
    service = Column( String, default="OpenSearch" )
    created_at = Column( DateTime, default=datetime.utcnow )
    resolved = Column( Boolean, default=False )

class IrrelevantQuestion(Base):
    __tablename__ = "irrelevant_questions"
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    question = Column(
        Text,
        nullable=False
    )
    reason = Column(
        String
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

from sqlalchemy import Column, Integer, Boolean, DateTime
from datetime import datetime, UTC
class ChatbotSettings(Base):
    __tablename__ = "chatbot_settings"

    id = Column(Integer, primary_key=True, index=True)

    # Global chatbot availability
    enabled = Column(Boolean, nullable=False, default=True)

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )
