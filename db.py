import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ism_user:ism_password@localhost:5432/ism_db"
    )
    
    class Config:
        env_file = ".env"


settings = Settings()

# Database engine
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables (use with caution)"""
    Base.metadata.drop_all(bind=engine)
