import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def truncate_tables():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE endpoints CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE organizations CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE users CASCADE;"))
    await engine.dispose()
    print("Truncated tables")

if __name__ == "__main__":
    asyncio.run(truncate_tables())
