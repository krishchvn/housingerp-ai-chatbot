import os
import re
import json
from typing import List

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from models.complaint import AIClassifiedComplaint, ComplaintCategory, ComplaintCreate, TextToSQLResult

load_dotenv()

_llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


def _build_classification_prompt(categories: List[ComplaintCategory]) -> str:
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

If the input is gibberish, too vague, or completely unrelated to housing complaints, set confidence below 0.4.

Return ONLY the JSON. No explanation."""


async def classify_complaint(
    user_message: str,
    categories: List[ComplaintCategory],
) -> AIClassifiedComplaint:
    """Use LLM to classify a user's complaint into a category."""
    system_prompt = _build_classification_prompt(categories)

    response = _llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ])

    raw = response.content.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"LLM returned no JSON object: {raw[:200]}")
    data = json.loads(match.group())
    if not isinstance(data, dict):
        raise ValueError(f"LLM returned unexpected format: {type(data).__name__}. Expected a JSON object.")
    return AIClassifiedComplaint(**data)


_COMPLAINTS_SCHEMA = """
Table: ai_complaints
Columns:
  - queriesComplaintId : SERIAL PRIMARY KEY
  - reqNumber          : VARCHAR  — unique request number e.g. REQ4C042F
  - societyId          : INTEGER
  - buildingId         : INTEGER
  - flatId             : INTEGER
  - userId             : INTEGER
  - complaintCategoryId: INTEGER
  - subject            : VARCHAR  — short title
  - description        : TEXT     — full description
  - complaintComments  : TEXT     — original user message
  - status             : INTEGER  — 0=New, 1=InProgress, 2=Resolved
  - aiClassifiedCategory: VARCHAR — category name
  - aiConfidenceScore  : FLOAT
  - isActive           : BOOLEAN
  - isDeleted          : BOOLEAN
  - createdOn          : TIMESTAMPTZ
  - updatedOn          : TIMESTAMPTZ
"""


async def text_to_sql(natural_language: str, categories: List[ComplaintCategory]) -> TextToSQLResult:
    """
    Convert a natural language query into a SQL SELECT and optionally
    identify if the query targets another user by name.
    """
    category_list = "\n".join(
        [f"  - {c.complaintCategoryId}: {c.complaintName}" for c in categories]
    )

    response = _llm.invoke([
        SystemMessage(content=f"""You are a SQL assistant for a housing society complaint system.

{_COMPLAINTS_SCHEMA}

Available complaint categories (use these to map user intent to the correct category name):
{category_list}

Status values (use these to map user intent to the correct integer):
  0 = Opened
  1 = In Progress
  2 = Completed
  3 = Declined

Convert the user's natural language query into a safe PostgreSQL SELECT statement.

Rules:
- ALWAYS include: WHERE userId = :userId AND societyId = :societyId
- Only SELECT from ai_complaints — no JOINs to other tables
- Use only columns listed in the schema above
- Identify the primary filter being applied and classify it as one of:
    "user"      — filtering by a person's name (e.g. "by Aarav Sharma")
    "category"  — filtering by complaint category (e.g. "maid issue" → "Cleaning Issue")
    "status"    — filtering by status value (e.g. "open"=0, "in progress"=1, "completed"=2, "declined"=3)
    "flatid"    — filtering by flat number
    "buildingid"— filtering by building
    "societyid" — filtering by society
    "subject"   — filtering by complaint subject text
    null        — no specific filter, general query

- For "user" filter: generate SQL using :userId and :societyId (the router will inject the correct userId after name lookup)
- For "category" filter: map the user's words to the closest category from the list above, then filter using complaintCategoryId = <id> (use the integer id, not the name string)
- For "status" filter: map the user's words to the correct integer (0/1/2/3) and embed in WHERE clause
- For all other filters: embed the filter directly in the SQL WHERE clause

- Return ONLY a valid JSON object:
  {{
    "sql": "<full SELECT statement with :userId and :societyId placeholders>",
    "filter_type": "<user|category|status|flatid|buildingid|societyid|subject|null>",
    "filter_value": "<the extracted value, or null>"
  }}
No explanation. No markdown."""),
        HumanMessage(content=natural_language),
    ])

    raw = response.content.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"LLM returned no JSON object: {raw[:200]}")
    data = json.loads(match.group())
    return TextToSQLResult(**data)


def build_complaint_payload(
    classified: AIClassifiedComplaint,
    user_message: str,
    user_context: dict,
) -> ComplaintCreate:
    """Convert AI classification + user context into a ComplaintCreate payload."""
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
