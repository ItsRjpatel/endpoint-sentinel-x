import asyncio
from sqlalchemy import select
from app.db.models.enrollment_token import EnrollmentToken
from app.db.session import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        token = (await db.execute(select(EnrollmentToken).order_by(EnrollmentToken.created_at.desc()))).scalars().first()
        print(token.id, token.token_value, token.uses_count, token.max_uses, token.is_active)

asyncio.run(main())
