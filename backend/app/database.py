import asyncio
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


DATABASE_URL = settings.AZURE_SQL_CONNECTION_STRING

async_engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

async_session_factory = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def async_main():
    """
    Initializes the database by creating all tables.
    """
    print("Initializing database tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialization complete.")


if __name__ == "__main__":
    # Important, running this file creates the database.
    try:
        asyncio.run(async_main())
    except Exception as e:
        print(f"An error occurred during database initialization: {e}")
