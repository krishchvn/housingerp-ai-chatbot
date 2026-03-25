from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    role: str        # 'user' | 'assistant'
    content: str
    intent: Optional[str] = None   # 'complaint' | 'document_qa' | 'general'


class ChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None
    userId: int
    societyId: int
    buildingId: Optional[int] = None
    flatId: Optional[int] = None
    authToken: str                  # forward JWT to HousingERP API


class ChatResponse(BaseModel):
    reply: str
    intent: str
    sessionId: str
    complaintDraft: Optional[dict] = None


class UserContext(BaseModel):
    """Pre-loaded user context fetched from HousingERP profile API."""
    userId: int
    firstName: str
    lastName: str
    societyId: int
    buildingId: Optional[int] = None
    flatId: Optional[int] = None
    email: Optional[str] = None
