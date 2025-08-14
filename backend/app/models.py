from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class RFPStatus(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    GENERATING_PRESENTATION = "generating_presentation"
    COMPLETED = "completed"
    FAILED = "failed"


class QuestionStatus(enum.Enum):
    EXTRACTED = "extracted"
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    SKIPPED = "skipped"
    FAILED = "failed"


class RFP(Base):
    __tablename__ = "rfps"

    rfp_id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True, nullable=False)
    storage_path = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    questions = relationship("Question", back_populates="rfp")
    presentations = relationship("Presentation", back_populates="rfp")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(Enum(RFPStatus), default=RFPStatus.UPLOADED, nullable=False)

    def __repr__(self):
        return f"<RFP(rfp_id={self.rfp_id}, filename='{self.filename}', status='{self.status.value}')>"


class Question(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True)
    rfp_id = Column(Integer, ForeignKey("rfps.rfp_id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_context = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    rfp = relationship("RFP", back_populates="questions")
    llm_responses = relationship("LLMResponse", back_populates="question")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(
        Enum(QuestionStatus), default=QuestionStatus.EXTRACTED, nullable=False
    )

    def __repr__(self):
        return f"<Question(question_id={self.question_id}, rfp_id={self.rfp_id}, status='{self.status.value}', text='{self.question_text[:50]}...')>"


class LLMResponse(Base):
    __tablename__ = "llm_responses"

    response_id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.question_id"), nullable=False)
    model_id = Column(String(100), nullable=True)
    retrieved_context = Column(Text, nullable=True)
    response = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    retrieval_time_ms = Column(Integer, nullable=True)
    generation_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    question = relationship("Question", back_populates="llm_responses")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String(50), default="initial_draft", nullable=False)


class Evaluation(Base):
    __tablename__ = "evaluations"

    eval_id = Column(Integer, primary_key=True, index=True)
    response_id = Column(
        Integer, ForeignKey("llm_responses.response_id"), nullable=False
    )
    original_response = Column(Text, nullable=True)
    fine_tuned_response = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    sme_comments = Column(Text, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
    llm_response = relationship("LLMResponse")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Presentation(Base):
    __tablename__ = "presentations"

    presentation_id = Column(Integer, primary_key=True, index=True)
    rfp_id = Column(Integer, ForeignKey("rfps.rfp_id"), nullable=False)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(255), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    generation_time_s = Column(Integer, nullable=True)
    rfp = relationship("RFP", back_populates="presentations")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
