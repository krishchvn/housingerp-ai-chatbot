from fastapi import APIRouter, HTTPException

from models.complaint import ComplaintTextRequest, ComplaintTextResponse, ComplaintQueryRequest, ComplaintQueryResponse
from services.complaint_service import classify_complaint, build_complaint_payload, text_to_sql
from services.sql_validator import validate_and_raise
from db.repositories.complaint_repo import insert_complaint, get_categories, run_query, enrich_complaint_rows
from db.repositories.user_repo import get_first_user, get_user_by_name

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintTextResponse)
async def create_complaint_from_text(request: ComplaintTextRequest):
    """
    Convert plain text into a structured complaint, save to DB, and return the JSON.
    User context is fetched from ai_users (hardcoded to first user until login/session is added).
    """
    user = get_first_user()
    if not user:
        raise HTTPException(status_code=404, detail="No active user found in ai_users")

    categories = get_categories(user.societyId)
    if not categories:
        raise HTTPException(status_code=404, detail=f"No categories found for societyId={user.societyId}")

    try:
        classified = await classify_complaint(request.text, categories)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"LLM classification failed: {e}")

    if classified.confidence < 0.4:
        return ComplaintTextResponse(
            reqNumber="", category="", categoryId=0,
            urgency="", subject="", description="",
            confidence=classified.confidence,
            savedToDb=False,
            needsClarification=True,
            clarificationMessage="I couldn't understand your complaint. Could you please describe the issue more clearly?",
        )

    payload = build_complaint_payload(
        classified,
        request.text,
        {
            "buildingId": user.buildingId,
            "flatId":     user.flatId,
            "societyId":  user.societyId,
            "userId":     user.userId,
        },
    )

    draft = {
        **payload.model_dump(),
        "aiClassifiedCategory": classified.category_name,
        "aiConfidenceScore":    classified.confidence,
        "aiRawInput":           request.text,
    }

    complaint_id = None
    saved = False
    try:
        complaint_id = insert_complaint(draft)
        saved = True
    except Exception as e:
        print(f"⚠️  Supabase insert failed: {e}")

    return ComplaintTextResponse(
        reqNumber=draft["reqNumber"],
        category=classified.category_name,
        categoryId=classified.category_id,
        urgency=classified.urgency,
        subject=classified.subject,
        description=classified.description,
        confidence=classified.confidence,
        savedToDb=saved,
        queriesComplaintId=complaint_id,
    )


@router.post("/query", response_model=ComplaintQueryResponse)
async def query_complaints(request: ComplaintQueryRequest):
    """
    Convert a natural language question into SQL, execute it, and return results.
    Defaults to current user. If another user is mentioned by name, looks them up in ai_users.
    """
    current_user = get_first_user()
    if not current_user:
        raise HTTPException(status_code=404, detail="No active user found in ai_users")

    categories = get_categories(current_user.societyId)
    try:
        result = await text_to_sql(request.query, categories)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse query: {e}")
    validate_and_raise(result.sql)

    # Only "user" filter_type requires a name lookup.
    # All other filter types (category, status, flatid, etc.) are handled in the SQL.
    if result.filter_type == "user" and result.filter_value:
        user = get_user_by_name(result.filter_value)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User '{result.filter_value}' not found.",
            )
    else:
        user = current_user

    try:
        rows = run_query(result.sql, user.userId, user.societyId)
        rows = enrich_complaint_rows(rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {e}")

    count = len(rows)
    message = (
        f"Found {count} complaint(s) for {user.firstName} {user.lastName}."
        if count > 0
        else "No complaints found matching your query."
    )

    return ComplaintQueryResponse(
        results=rows,
        count=count,
        message=message,
        sql=result.sql,
    )
