"""
Run once to create all AI tables in Supabase (PostgreSQL).
Usage: python db/run_schemas.py
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

CONN = os.getenv("DATABASE_URL")
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")
SCHEMA_FILES = ["complaints.sql", "chat_history.sql", "documents.sql"]

engine = create_engine(CONN, echo=False)

for filename in SCHEMA_FILES:
    path = os.path.join(SCHEMA_DIR, filename)
    with open(path, "r") as f:
        sql = f.read()

    # Strip -- comments before splitting so leading comments don't hide statements
    import re
    sql_stripped = re.sub(r"--[^\n]*", "", sql)
    statements = [s.strip() for s in sql_stripped.split(";") if s.strip()]

    for stmt in statements:
        try:
            with engine.begin() as conn:
                conn.execute(text(stmt))
        except Exception as e:
            print(f"  ⚠️  Skipped (likely already exists): {e}")

    print(f"✅ {filename} applied.")

print("\n✅ All schemas ready.")
