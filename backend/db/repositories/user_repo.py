from typing import Optional
from sqlalchemy import text
from db.connection import engine
from models.user import User


def get_user_by_name(name: str) -> Optional[User]:
    """Look up a user by first or last name in ai_users."""
    sql = text("""
        SELECT userId, societyId, buildingId, flatId, firstName, lastName, sex, status
        FROM ai_users
        WHERE status = 1
          AND (
            LOWER(firstName) = LOWER(:name)
            OR LOWER(lastName) = LOWER(:name)
            OR LOWER(CONCAT(firstName, ' ', lastName)) = LOWER(:name)
          )
        ORDER BY userId
        LIMIT 1
    """)
    with engine.connect() as conn:
        row = conn.execute(sql, {"name": name}).fetchone()

    if not row:
        return None

    return User(
        userId=row[0],
        societyId=row[1],
        buildingId=row[2],
        flatId=row[3],
        firstName=row[4],
        lastName=row[5],
        sex=row[6],
        status=row[7],
    )


def find_user_in_text(query: str) -> Optional[User]:
    """
    Scan all active users and check if any name appears in the query text.
    Checks full name, first name, and last name (case-insensitive).
    Used as a fallback when the LLM doesn't extract target_user reliably.
    """
    sql = text("""
        SELECT userId, societyId, buildingId, flatId, firstName, lastName, sex, status
        FROM ai_users
        WHERE status = 1
        ORDER BY userId
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql).fetchall()

    query_lower = query.lower()
    for row in rows:
        full_name  = f"{row[4]} {row[5]}".lower()
        first_name = row[4].lower()
        last_name  = row[5].lower()
        if full_name in query_lower or first_name in query_lower or last_name in query_lower:
            return User(
                userId=row[0], societyId=row[1], buildingId=row[2],
                flatId=row[3], firstName=row[4], lastName=row[5],
                sex=row[6], status=row[7],
            )
    return None


def get_first_user() -> Optional[User]:
    """
    Fetch the first active user from ai_users.
    Temporary — will be replaced by session-based lookup after login is implemented.
    """
    sql = text("""
        SELECT userId, societyId, buildingId, flatId, firstName, lastName, sex, status
        FROM ai_users
        WHERE status = 1
        ORDER BY userId
        LIMIT 1
    """)
    with engine.connect() as conn:
        row = conn.execute(sql).fetchone()

    if not row:
        return None

    return User(
        userId=row[0],
        societyId=row[1],
        buildingId=row[2],
        flatId=row[3],
        firstName=row[4],
        lastName=row[5],
        sex=row[6],
        status=row[7],
    )
