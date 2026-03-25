import os
import uuid
import httpx
from typing import List, Optional

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

from models.chat import ChatRequest, ChatResponse, UserContext
from models.complaint import ComplaintCategory
from services.complaint_service import classify_complaint, build_complaint_payload
from db.repositories.complaint_repo import insert_complaint

load_dotenv()

_llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),
)

# In-memory session store (replace with DB-backed sessions when adding chat history)
_sessions: dict = {}


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _detect_intent(message: str) -> str:
    """Classify message into: complaint | document_qa | general."""
    response = _llm.invoke([
        SystemMessage(content="""Classify this message into exactly one of: complaint, document_qa, general.
Return only the single word. No explanation."""),
        HumanMessage(content=message),
    ])
    intent = response.content.strip().lower()
    return intent if intent in ("complaint", "document_qa", "general") else "general"


async def _fetch_user_context(auth_token: str, user_id: int) -> Optional[UserContext]:
    """Fetch user profile from HousingERP API."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                f"{os.getenv('HOUSINGERP_API_BASE')}/user",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            if res.status_code == 200:
                data = res.json()
                return UserContext(
                    userId=data.get("userId", user_id),
                    firstName=data.get("firstName", "Resident"),
                    lastName=data.get("lastName", ""),
                    societyId=data.get("societyId"),
                    buildingId=data.get("buildingId"),
                    flatId=data.get("flatId"),
                    email=data.get("email"),
                )
    except Exception:
        pass
    return None


async def _fetch_complaint_categories(
    auth_token: str, society_id: int
) -> List[ComplaintCategory]:
    """Fetch complaint categories from HousingERP API, with hardcoded fallback."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                f"{os.getenv('HOUSINGERP_API_BASE')}/complaint-categories",
                headers={"Authorization": f"Bearer {auth_token}"},
                params={"societyId": society_id},
            )
            if res.status_code == 200:
                return [ComplaintCategory(**c) for c in res.json()]
    except Exception:
        pass

    return [
        ComplaintCategory(complaintCategoryId=4,  complaintName="Water issue"),
        ComplaintCategory(complaintCategoryId=5,  complaintName="Electricity Issue"),
        ComplaintCategory(complaintCategoryId=6,  complaintName="Fund Issues"),
        ComplaintCategory(complaintCategoryId=7,  complaintName="Telecom issue"),
        ComplaintCategory(complaintCategoryId=8,  complaintName="Light issue"),
        ComplaintCategory(complaintCategoryId=22, complaintName="Cleaning Issue"),
    ]


def _save_complaint_to_db(draft: dict) -> Optional[int]:
    """Insert complaint into Supabase. Returns new ID or None on failure."""
    try:
        complaint_id = insert_complaint(draft)
        print(f"✅ Complaint saved to Supabase: queriesComplaintId={complaint_id}")
        return complaint_id
    except Exception as e:
        print(f"⚠️  Supabase insert failed: {e}")
        return None


# ── Main entry point ──────────────────────────────────────────────────────────

async def process_chat(request: ChatRequest) -> ChatResponse:
    session_id = request.sessionId or str(uuid.uuid4())

    if session_id not in _sessions:
        _sessions[session_id] = {"history": []}

    history: List = _sessions[session_id]["history"]

    # Resolve user context
    user = await _fetch_user_context(request.authToken, request.userId)
    if not user:
        user = UserContext(
            userId=request.userId,
            firstName="Resident",
            lastName="",
            societyId=request.societyId,
            buildingId=request.buildingId,
            flatId=request.flatId,
        )

    intent = await _detect_intent(request.message)

    # ── Complaint: classify → save → done ────────────────────────────────────
    if intent == "complaint":
        categories = await _fetch_complaint_categories(request.authToken, user.societyId)
        classified = await classify_complaint(request.message, categories)
        payload = build_complaint_payload(
            classified,
            request.message,
            {
                "buildingId": user.buildingId or request.buildingId,
                "flatId":     user.flatId or request.flatId,
                "societyId":  user.societyId,
                "userId":     user.userId,
            },
        )
        draft = {
            **payload.model_dump(),
            "aiClassifiedCategory": classified.category_name,
            "aiConfidenceScore":    classified.confidence,
            "aiRawInput":           request.message,
        }

        _save_complaint_to_db(draft)

        urgency_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "🚨"}.get(
            classified.urgency, "🔵"
        )
        return ChatResponse(
            reply=(
                f"Your complaint has been raised!\n\n"
                f"📋 **Category:** {classified.category_name}\n"
                f"{urgency_emoji} **Urgency:** {classified.urgency.capitalize()}\n"
                f"📝 **Subject:** {classified.subject}\n"
                f"🔖 **Request No:** {draft['reqNumber']}\n\n"
                f"The maintenance team will be in touch soon."
            ),
            intent="complaint",
            sessionId=session_id,
            complaintDraft=draft,
        )

    # ── General / document_qa ─────────────────────────────────────────────────
    history.append(HumanMessage(content=request.message))
    messages = [SystemMessage(content="""You are a helpful assistant for a housing society management platform (HousingERP).
Be warm, concise, and helpful.""")] + history[-10:]
    response = _llm.invoke(messages)
    history.append(AIMessage(content=response.content))

    return ChatResponse(
        reply=response.content,
        intent=intent,
        sessionId=session_id,
    )
