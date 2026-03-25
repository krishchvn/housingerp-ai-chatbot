from typing import Dict, List
from sqlalchemy import text
from db.connection import engine


def get_status_map(status_ids: List[int]) -> Dict[int, str]:
    """
    Batch-fetch status names for a list of status IDs.
    Returns {statusId: statusName} e.g. {0: "Opened", 1: "In Progress"}.
    """
    if not status_ids:
        return {}

    sql = text("""
        SELECT statusId, statusName
        FROM ai_status
        WHERE statusId = ANY(:ids)
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql, {"ids": status_ids}).fetchall()

    return {r[0]: r[1] for r in rows}


def get_all_statuses() -> List[Dict]:
    """
    Fetch all statuses from ai_status.
    Returns list of {statusId, statusName} dicts.
    Useful for building LLM prompts.
    """
    sql = text("SELECT statusId, statusName FROM ai_status ORDER BY statusId")
    with engine.connect() as conn:
        rows = conn.execute(sql).fetchall()
    return [{"statusId": r[0], "statusName": r[1]} for r in rows]
