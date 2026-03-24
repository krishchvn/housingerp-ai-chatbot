from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

SQLSERVER_CONN = os.getenv("SQLSERVER_CONN")

engine = create_engine(
    SQLSERVER_CONN,
    echo=False,
    pool_pre_ping=True,       # auto-reconnect if connection drops
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Call this on startup to verify DB is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ SQL Server connected successfully.")
    except Exception as e:
        print(f"❌ SQL Server connection failed: {e}")
        print("   Make sure Docker is running: docker-compose up -d")
        raise


def create_database_if_not_exists():
    """
    Creates the HousingERPAI database if it doesn't exist.
    Connects to master DB first, then switches.
    """
    master_conn = SQLSERVER_CONN.replace("/HousingERPAI", "/master")
    master_engine = create_engine(master_conn, echo=False, isolation_level="AUTOCOMMIT")
    db_name = os.getenv("SQLSERVER_DB", "HousingERPAI")

    try:
        with master_engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT name FROM sys.databases WHERE name = '{db_name}'")
            )
            if not result.fetchone():
                conn.execute(text(f"CREATE DATABASE [{db_name}]"))
                print(f"✅ Database '{db_name}' created.")
            else:
                print(f"✅ Database '{db_name}' already exists.")
    except Exception as e:
        print(f"❌ Could not create database: {e}")
        raise
    finally:
        master_engine.dispose()
