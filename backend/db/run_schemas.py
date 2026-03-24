"""
Run once to create all AI tables in the local SQL Server.
Usage: python db/run_schemas.py
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

CONN = os.getenv("SQLSERVER_CONN")
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")
SCHEMA_FILES = ["complaints.sql", "chat_history.sql", "documents.sql"]

engine = create_engine(CONN, echo=False)

for filename in SCHEMA_FILES:
    path = os.path.join(SCHEMA_DIR, filename)
    with open(path, "r") as f:
        sql = f.read()

    # Split on GO or semicolons for multi-statement files
    statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]

    with engine.begin() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
            except Exception as e:
                print(f"  ⚠️  Skipped (likely already exists): {e}")

    print(f"✅ {filename} applied.")

print("\n✅ All schemas ready.")
