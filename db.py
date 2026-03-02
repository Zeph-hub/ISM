import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings (database connection only). Extras ignored."""
    database_url: str = os.getenv(
        "DATABASE_URL",
        # default to development credentials (can be overridden via env)
        "postgresql://root:root1@localhost:5432/ISM"
    )

    # ignore unrelated environment variables coming from .env files
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

    # optionally allow building URL from components
    @classmethod
    def from_components(cls):
        db_user = os.getenv("DB_USER", "root")
        db_pass = os.getenv("DB_PASS", "root1")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "ISM")
        url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        return cls(database_url=url)


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
