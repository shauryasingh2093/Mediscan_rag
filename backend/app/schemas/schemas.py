"""Pydantic schemas for request/response validation."""

from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# User schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Document schemas
class DocumentUpload(BaseModel):
    filename: str
    content_type: str


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Chat schemas
class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    sources: List[dict] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    title: Optional[str] = None
    patient_id: Optional[str] = None


class ChatSessionResponse(BaseModel):
    id: UUID
    title: Optional[str]
    patient_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Literature schemas
class PaperResponse(BaseModel):
    id: UUID
    pmid: str
    title: str
    abstract: Optional[str]
    authors: List[str]
    journal: Optional[str]
    publication_year: Optional[int]
    doi: Optional[str]
    
    class Config:
        from_attributes = True


# Image schemas
class ImageAnalysisResult(BaseModel):
    id: UUID
    prediction: str
    confidence: float
    findings: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Timeline schemas
class TimelineEventResponse(BaseModel):
    id: UUID
    event_date: datetime
    event_type: str
    content: str
    summary: Optional[str]
    
    class Config:
        from_attributes = True
