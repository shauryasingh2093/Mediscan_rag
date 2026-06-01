"""SQLAlchemy models for database tables."""

from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from backend.app.database.engine import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    timelines = relationship("PatientTimeline", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    """Uploaded medical document model."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_text = Column(Text)
    extracted_text = Column(Text)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    image_findings = relationship("ImageFinding", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Text chunks from documents for embeddings."""
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_number = Column(Integer, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    embedding_id = Column(String(255))  # Qdrant point ID
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")


class MedicalLiterature(Base):
    """Medical research papers from PubMed."""
    __tablename__ = "medical_literature"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    pmid = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    abstract = Column(Text)
    authors = Column(ARRAY(String), default=[])
    journal = Column(String(255))
    publication_year = Column(Integer)
    doi = Column(String(255))
    keywords = Column(ARRAY(String), default=[])
    embedding_id = Column(String(255))  # Qdrant point ID
    source = Column(String(50), default="pubmed")
    synced_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatSession(Base):
    """Chat conversation sessions."""
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    patient_id = Column(String(255))
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """Chat messages."""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(50), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=[])  # Citations/sources
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class ImageFinding(Base):
    """X-ray image analysis results."""
    __tablename__ = "image_findings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    image_path = Column(String(500), nullable=False)
    prediction = Column(String(100), nullable=False)  # "Normal", "Pneumonia", etc.
    confidence = Column(Float)
    findings = Column(Text)
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="image_findings")


class PatientTimeline(Base):
    """Patient progression timeline."""
    __tablename__ = "patient_timeline"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    patient_name = Column(String(255))
    event_date = Column(DateTime)
    event_type = Column(String(50))  # "report", "image", "note"
    content = Column(Text)
    associated_documents = Column(ARRAY(String), default=[])
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="timelines")
