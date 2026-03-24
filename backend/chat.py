import os
import uuid
import httpx
from typing import List, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from models.chat import ChatRequest, ChatResponse, UserContext
from models.complaint import ComplaintCategory
from complaint import classify_complaint, build_complaint_payload
from dotenv import load_dotenv

load_dotenv()

HOUSINGERP_API = os.getenv("HOUSINGERP_API_BASE")

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),
)

# In-memory session store (replace with SQL Server for production)
sessions: dict = {}


def get_system_prompt(user: UserContext, categories: List[ComplaintCategory]) -> str:
    cat_names = ", ".join([c.complaintName for c in categories])
    return f"""You are a helpful assistant for a housing society management platform (HousingERP).
You are talking to {user.firstName} {user.lastName}, resident of Flat {user.flatId}, Building {user.buildingId}.

You have TWO capabilities:
1. COMPLAINT: Help residents report maintenance issues (Water, Electricity, Cleaning, etc.)
2. DOCUMENT_QA: Answer questions about society rules, bylaws, and policies from uploaded documents.
3. GENERAL: Handle greetings and general questions.

Available complaint categories: {cat_names}

Rules:
- Be warm, concise, and helpful.
- For complaints: detect the issue, confirm category with resident, then say "Shall I raise this complaint?"
- For document questions: answer only from provided context. If unsure, say "I couldn't find this in our documents."
- Never make up society rules.
- Always confirm before submitting a complaint.

Respond naturally. Keep replies short and clear."""


async def detect_intent(message: str) -> str:
    """Quick intent detection — complaint, document_qa, or general."""
    response = llm.invoke([
        SystemMessage(content="""Classify this message into exactly one of: complaint, document_qa, general.
Return only the single word. No explanation."""),
        HumanMessage(content=message),
    ])
    intent = response.content.strip().lower()
    if intent not in ("complaint", "document_qa", "general"):
        return "general"
    return intent


async def fetch_user_context(auth_token: str, user_id: int) -> Optional[UserContext]:
    """Fetch user profile from HousingERP API."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                f"{HOUSINGERP_API}/user",
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


async def fetch_complaint_categories(auth_token: str, society_id: int) -> List[ComplaintCategory]:
    """Fetch complaint categories from HousingERP API."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                f"{HOUSINGERP_API}/complaint-categories",
                headers={"Authorization": f"Bearer {auth_token}"},
                params={"societyId": society_id},
            )
            if res.status_code == 200:
                return [ComplaintCategory(**c) for c in res.json()]
    except Exception:
        pass
    # Fallback hardcoded categories (from UI screenshots)
    return [
        ComplaintCategory(complaintCategoryId=4, complaintName="Water issue"),
        ComplaintCategory(complaintCategoryId=5, complaintName="Electricity Issue"),
        ComplaintCategory(complaintCategoryId=6, complaintName="Fund Issues"),
        ComplaintCategory(complaintCategoryId=7, complaintName="Telecom issue"),
        ComplaintCategory(complaintCategoryId=8, complaintName="Light issue"),
        ComplaintCategory(complaintCategoryId=22, complaintName="Cleaning Issue"),
    ]


async def submit_complaint(payload: dict, auth_token: str) -> dict:
    """POST complaint to HousingERP API."""
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.post(
            f"{HOUSINGERP_API}/queries-complaints",
            json=payload,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        res.raise_for_status()
        return res.json()


async def process_chat(request: ChatRequest) -> ChatResponse:
    session_id = request.sessionId or str(uuid.uuid4())

    # Init session if new
    if session_id not in sessions:
        sessions[session_id] = {"history": [], "complaint_draft": None}

    session = sessions[session_id]
    history: List = session["history"]

    # Fetch context
    user = await fetch_user_context(request.authToken, request.userId)
    if not user:
        user = UserContext(
            userId=request.userId,
            firstName="Resident",
            lastName="",
            societyId=request.societyId,
            buildingId=request.buildingId,
            flatId=request.flatId,
        )

    categories = await fetch_complaint_categories(request.authToken, user.societyId)

    # Detect intent
    intent = await detect_intent(request.message)

    # Handle complaint confirmation
    msg_lower = request.message.strip().lower()
    if session["complaint_draft"] and msg_lower in ("yes", "yeah", "sure", "ok", "okay", "submit", "confirm"):
        try:
            result = await submit_complaint(session["complaint_draft"], request.authToken)
            req_num = result.get("reqNumber", session["complaint_draft"].get("reqNumber"))
            session["complaint_draft"] = None
            return ChatResponse(
                reply=f"Complaint raised successfully! Your request number is **{req_num}**. The maintenance team will be in touch soon.",
                intent="complaint",
                sessionId=session_id,
                requiresConfirmation=False,
            )
        except Exception as e:
            return ChatResponse(
                reply=f"Sorry, I couldn't submit the complaint right now. Please try again or use the complaints form directly.",
                intent="complaint",
                sessionId=session_id,
            )

    if session["complaint_draft"] and msg_lower in ("no", "cancel", "nope", "don't"):
        session["complaint_draft"] = None
        return ChatResponse(
            reply="No problem! Let me know if there's anything else I can help with.",
            intent="general",
            sessionId=session_id,
        )

    # Process complaint intent
    if intent == "complaint":
        classified = await classify_complaint(request.message, categories)
        payload = build_complaint_payload(
            classified,
            request.message,
            {
                "buildingId": user.buildingId or request.buildingId,
                "flatId": user.flatId or request.flatId,
                "societyId": user.societyId,
                "userId": user.userId,
            },
        )
        session["complaint_draft"] = payload.model_dump()

        urgency_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "🚨"}.get(classified.urgency, "🔵")
        reply = (
            f"I've identified your issue:\n\n"
            f"📋 **Category:** {classified.category_name}\n"
            f"{urgency_emoji} **Urgency:** {classified.urgency.capitalize()}\n"
            f"📝 **Subject:** {classified.subject}\n\n"
            f"Shall I raise this complaint on your behalf? (Yes / No)"
        )
        return ChatResponse(
            reply=reply,
            intent="complaint",
            sessionId=session_id,
            complaintDraft=session["complaint_draft"],
            requiresConfirmation=True,
        )

    # General conversation fallback
    system_prompt = get_system_prompt(user, categories)
    history.append(HumanMessage(content=request.message))

    messages = [SystemMessage(content=system_prompt)] + history[-10:]  # keep last 10 messages
    response = llm.invoke(messages)
    history.append(AIMessage(content=response.content))

    return ChatResponse(
        reply=response.content,
        intent=intent,
        sessionId=session_id,
    )
