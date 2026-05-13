from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

#The engine is main connection point between our FastAPI app and the database.
#It uses DATABASE_URL from our .env file to connect to the database.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # This is needed for SQLite databases to allow multiple threads to access the database.
)

#SessionLocal creates database sessions.
#A session is like a temporary conversation with the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base is the parent class for all our database models.
#Every table class we create will inherit from Base.
Base = declarative_base()

def get_db():
    #This function is a dependency that we will use in our API endpoints to get a database session.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()