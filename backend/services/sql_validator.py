import re
from fastapi import HTTPException

# Keywords that must never appear in LLM-generated SQL
_FORBIDDEN = {"insert", "update", "delete", "drop", "truncate", "alter", "create", "grant", "revoke", "union"}

# SQL injection markers
_INJECTION_PATTERNS = [r"--", r"/\*", r"\*/", r";\s*\w"]


def validate_select_only(sql: str) -> bool:
    """Returns True if the SQL is a SELECT statement and contains no forbidden keywords."""
    clean = sql.strip().lower()

    if not clean.startswith("select"):
        return False

    tokens = set(re.findall(r"\b\w+\b", clean))
    if tokens & _FORBIDDEN:
        return False

    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, clean):
            return False

    return True


def validate_user_scope(sql: str) -> bool:
    """Returns True if the SQL contains :userId and :societyId placeholders."""
    return ":userid" in sql.lower() and ":societyid" in sql.lower()


def validate_and_raise(sql: str) -> None:
    """
    Validates the SQL is safe to execute.
    Raises HTTPException 400 if any check fails.
    Reusable across complaints, billing, expenses, etc.
    """
    if not validate_select_only(sql):
        raise HTTPException(
            status_code=400,
            detail="Invalid query: only SELECT statements are allowed.",
        )

    if not validate_user_scope(sql):
        raise HTTPException(
            status_code=400,
            detail="Invalid query: missing required user scope filters.",
        )
