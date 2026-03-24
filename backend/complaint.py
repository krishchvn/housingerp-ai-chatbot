import os
import json
from typing import List
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from models.complaint import ComplaintCreate, AIClassifiedComplaint, ComplaintCategory
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


def build_classification_prompt(categories: List[ComplaintCategory]) -> str:
    cat_list = "\n".join(
        [f"  - id: {c.complaintCategoryId}, name: {c.complaintName}" for c in categories]
    )
    return f"""You are a housing society maintenance assistant.

Given a resident's complaint message, return ONLY a valid JSON object with these fields:
{{
  "category_name": "<exact name from list>",
  "category_id": <integer id from list>,
  "urgency": "<low|medium|high|critical>",
  "subject": "<short 5-8 word title>",
  "description": "<clean 1-2 sentence description>",
  "confidence": <float 0.0 to 1.0>
}}

Available complaint categories:
{cat_list}

Urgency guide:
  - critical: safety hazard, no water/power for building, lift stuck with person
  - high: water leak, power outage in flat, lift not working
  - medium: intermittent issues, partial services affected
  - low: cosmetic, minor inconvenience

Return ONLY the JSON. No explanation."""


async def classify_complaint(
    user_message: str,
    categories: List[ComplaintCategory],
) -> AIClassifiedComplaint:
    """Use LLM to classify a user's complaint into a category."""
    system_prompt = build_classification_prompt(categories)

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ])

    raw = response.content.strip()
    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    return AIClassifiedComplaint(**data)


def build_complaint_payload(
    classified: AIClassifiedComplaint,
    user_message: str,
    user_context: dict,
) -> ComplaintCreate:
    """Convert AI classification + user context into ComplaintCreate payload."""
    return ComplaintCreate(
        buildingId=user_context["buildingId"],
        flatId=user_context["flatId"],
        societyId=user_context["societyId"],
        userId=user_context["userId"],
        createdBy=user_context["userId"],
        updatedBy=user_context["userId"],
        complaintCategoryId=classified.category_id,
        subject=classified.subject,
        description=classified.description,
        complaintComments=user_message,
    )
