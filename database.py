import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

if SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"connect_timeout": 30},  # allows Neon database cold-start warmup
        pool_size=10,
        max_overflow=20,
        pool_recycle=300
    )
else:
    # Fallback/Error
    raise ValueError("DATABASE_URL environment variable is not set")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency that yields a database session and handles retries on Neon cold-start."""
    max_retries = 3
    for attempt in range(max_retries):
        db = SessionLocal()
        try:
            yield db
            return
        except Exception as e:
            db.close()
            err = str(e).lower()
            is_connection_err = any(k in err for k in [
                "connection", "operational", "timeout", "ssl", "could not connect",
                "server closed", "eof", "connection reset"
            ])
            if is_connection_err and attempt < max_retries - 1:
                print(f"[DB] Connection failed (attempt {attempt + 1}/{max_retries}), retrying in 2s...")
                time.sleep(2)
                continue
            raise
        finally:
            try:
                db.close()
            except Exception:
                pass

def warmup_db():
    """Ping the database once to wake up Neon serverless instance on startup."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("[DB] Neon database connection warmed up successfully.")
    except Exception as e:
        print(f"[DB] Warmup ping failed (Neon may still be waking up): {e}")
