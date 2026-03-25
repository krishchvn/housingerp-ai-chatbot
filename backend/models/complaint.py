from pydantic import BaseModel, Field, field_validator
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


# ── Text-to-JSON complaint endpoint ─────────────────────────────

class ComplaintTextRequest(BaseModel):
    """Plain text input from the user."""
    text: str


class ComplaintTextResponse(BaseModel):
    """Structured JSON returned after classification and DB insert."""
    reqNumber: str
    category: str
    categoryId: int
    urgency: str
    subject: str
    description: str
    confidence: float
    savedToDb: bool
    queriesComplaintId: Optional[int] = None
    needsClarification: bool = False
    clarificationMessage: Optional[str] = None


# ── Text-to-SQL query endpoint ───────────────────────────────────

class TextToSQLResult(BaseModel):
    """Internal result from the LLM text-to-SQL conversion."""
    sql: str
    filter_type: Optional[str] = None   # user | flatid | buildingid | societyid | subject | category | status | None
    filter_value: Optional[str] = None  # extracted value (e.g. "Aarav Sharma", "Light issue", "0")

    @field_validator("filter_value", mode="before")
    @classmethod
    def coerce_to_str(cls, v):
        return str(v) if v is not None else None


class ComplaintQueryRequest(BaseModel):
    """Natural language query from the user."""
    query: str


class ComplaintQueryResponse(BaseModel):
    """Results of a natural language complaint query."""
    results: List[dict]
    count: int
    message: str
    sql: str                            # exposed for debugging; hide in production
