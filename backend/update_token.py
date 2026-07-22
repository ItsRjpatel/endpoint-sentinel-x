import asyncio
from sqlalchemy import select
from app.db.models.enrollment_token import EnrollmentToken
from app.db.session import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        token = (await db.execute(select(EnrollmentToken).where(EnrollmentToken.token_value == '3ac31f55-2e61-4dcf-bb40-e8f717480999'))).scalar_one()
        token.max_uses = 3
        token.uses_count = 0
        await db.commit()
        print('updated', token.max_uses, token.uses_count)

asyncio.run(main())
