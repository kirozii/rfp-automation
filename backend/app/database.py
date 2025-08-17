from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base


DATABASE_URL = settings.AZURE_SQL_CONNECTION_STRING

async_engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

async_session_factory = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()
