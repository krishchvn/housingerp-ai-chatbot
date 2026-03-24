from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class ComplaintCategory(BaseModel):
    complaintCategoryId: int
    complaintName: str


class ComplaintCreate(BaseModel):
    """Payload sent to HousingERP API to create a complaint."""
    buildingId: int
    flatId: int
    societyId: int
    userId: int
    createdBy: int
    updatedBy: int
    complaintCategoryId: int
    subject: str
    description: str
    complaintComments: str
    reqNumber: str = Field(default_factory=lambda: f"REQ{uuid.uuid4().hex[:6].upper()}")
    queriesComplaintGuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    createdOn: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updatedOn: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    isActive: bool = True
    isDeleted: bool = False
    status: int = 0
    process: int = 0
    userRating: int = 0
    tblComplaintComments: List = Field(default_factory=list)
    queriesComplaintImage: Optional[str] = None


class ComplaintResponse(BaseModel):
    queriesComplaintId: int
    reqNumber: str
    status: int
    message: str = "Complaint submitted successfully"


# ── AI classification result ────────────────────────────────────

class AIClassifiedComplaint(BaseModel):
    """What the LLM returns after classifying user input."""
    category_name: str
    category_id: int
    urgency: str           # low | medium | high | critical
    subject: str
    description: str
    confidence: float      # 0.0 - 1.0
