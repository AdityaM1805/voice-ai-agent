from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


connect_args = {}

# SQLite needs special threading config.
# PostgreSQL does not.
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """
    Creates database session for each request.

    FastAPI dependency injection automatically
    closes the DB connection after request completes.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()