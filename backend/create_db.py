import asyncio
from app.database import async_engine, Base, DATABASE_URL
from app import models


async def init_db():
    async with async_engine.begin() as conn:
        print(DATABASE_URL)
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Tables created successfully")


if __name__ == "__main__":
    asyncio.run(init_db())
