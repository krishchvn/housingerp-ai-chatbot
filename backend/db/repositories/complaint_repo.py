from typing import Optional, List
from sqlalchemy import text
from db.connection import engine
from models.complaint import ComplaintCategory
from db.repositories.status_repo import get_status_map


def insert_complaint(data: dict) -> Optional[int]:
    """
    Insert a complaint into ai_complaints.
    Returns the generated queriesComplaintId, or None on failure.
    """
    sql = text("""
        INSERT INTO ai_complaints (
            queriesComplaintGuid,
            reqNumber,
            societyId,
            buildingId,
            flatId,
            userId,
            createdBy,
            updatedBy,
            complaintCategoryId,
            subject,
            description,
            complaintComments,
            status,
            process,
            userRating,
            isActive,
            isDeleted,
            aiClassifiedCategory,
            aiConfidenceScore,
            aiRawInput,
            submittedViaChat
        ) VALUES (
            :queriesComplaintGuid,
            :reqNumber,
            :societyId,
            :buildingId,
            :flatId,
            :userId,
            :createdBy,
            :updatedBy,
            :complaintCategoryId,
            :subject,
            :description,
            :complaintComments,
            :status,
            :process,
            :userRating,
            :isActive,
            :isDeleted,
            :aiClassifiedCategory,
            :aiConfidenceScore,
            :aiRawInput,
            :submittedViaChat
        )
        RETURNING queriesComplaintId
    """)

    with engine.begin() as conn:
        result = conn.execute(sql, {
            "queriesComplaintGuid": data.get("queriesComplaintGuid"),
            "reqNumber":            data.get("reqNumber"),
            "societyId":            data["societyId"],
            "buildingId":           data["buildingId"],
            "flatId":               data["flatId"],
            "userId":               data["userId"],
            "createdBy":            data["createdBy"],
            "updatedBy":            data["updatedBy"],
            "complaintCategoryId":  data["complaintCategoryId"],
            "subject":              data.get("subject"),
            "description":          data.get("description"),
            "complaintComments":    data.get("complaintComments"),
            "status":               data.get("status", 0),
            "process":              data.get("process", 0),
            "userRating":           data.get("userRating", 0),
            "isActive":             data.get("isActive", True),
            "isDeleted":            data.get("isDeleted", False),
            "aiClassifiedCategory": data.get("aiClassifiedCategory"),
            "aiConfidenceScore":    data.get("aiConfidenceScore"),
            "aiRawInput":           data.get("aiRawInput"),
            "submittedViaChat":     data.get("submittedViaChat", True),
        })
        row = result.fetchone()
        return row[0] if row else None


def run_query(sql: str, user_id: int, society_id: int) -> List[dict]:
    """
    Execute a validated LLM-generated SELECT query scoped to a specific user.
    Returns rows as a list of dicts.
    """
    with engine.connect() as conn:
        result = conn.execute(
            text(sql),
            {"userId": user_id, "societyId": society_id},
        )
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]


def enrich_complaint_rows(rows: List[dict]) -> List[dict]:
    """
    Replace IDs with human-readable names in complaint query results.
    - createdby / updatedby / userid → firstName + lastName from ai_users
    - complaintcategoryid            → complaintName from ai_complaint_categories
    - status                         → statusName from ai_status (via status_repo)
    Column keys are lowercase (PostgreSQL default).
    """
    if not rows:
        return rows

    # Collect IDs to look up
    user_fields = {"createdby", "updatedby", "userid"}
    user_ids = {
        int(row[f])
        for row in rows
        for f in user_fields
        if f in row and row[f] is not None
    }
    cat_ids = {
        int(row["complaintcategoryid"])
        for row in rows
        if "complaintcategoryid" in row and row["complaintcategoryid"] is not None
    }
    status_ids = {
        int(row["status"])
        for row in rows
        if "status" in row and row["status"] is not None
    }

    with engine.connect() as conn:
        user_map: dict = {}
        if user_ids:
            result = conn.execute(
                text("SELECT userid, firstname, lastname FROM ai_users WHERE userid = ANY(:ids)"),
                {"ids": list(user_ids)},
            )
            user_map = {r[0]: f"{r[1]} {r[2]}" for r in result}

        cat_map: dict = {}
        if cat_ids:
            result = conn.execute(
                text("SELECT complaintcategoryid, complaintname FROM ai_complaint_categories WHERE complaintcategoryid = ANY(:ids)"),
                {"ids": list(cat_ids)},
            )
            cat_map = {r[0]: r[1] for r in result}

    status_map = get_status_map(list(status_ids))

    column_maps = {
        "createdby":           user_map,
        "updatedby":           user_map,
        "userid":              user_map,
        "complaintcategoryid": cat_map,
        "status":              status_map,
    }

    enriched = []
    for row in rows:
        r = dict(row)
        for col, lookup in column_maps.items():
            if col in r and r[col] is not None:
                r[col] = lookup.get(int(r[col]), str(r[col]))
        enriched.append(r)

    return enriched


def get_categories(society_id: int) -> List[ComplaintCategory]:
    """Fetch active complaint categories for a society from DB."""
    sql = text("""
        SELECT complaintCategoryId, complaintName
        FROM ai_complaint_categories
        WHERE societyId = :society_id AND isActive = true
        ORDER BY complaintCategoryId
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql, {"society_id": society_id}).fetchall()
    return [
        ComplaintCategory(complaintCategoryId=row[0], complaintName=row[1])
        for row in rows
    ]
