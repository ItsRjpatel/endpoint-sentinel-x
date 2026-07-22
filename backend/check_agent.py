import asyncio
from hashlib import sha256
from sqlalchemy import select
from app.db.models.endpoint import Endpoint
from app.db.session import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        ep = (await db.execute(select(Endpoint).where(Endpoint.agent_id == 'c7aa03b4-1935-4481-90fc-a97e0901bbd5'))).scalar_one_or_none()
        print('found', bool(ep))
        if ep:
            print('agent_id', ep.agent_id)
            print('secret_hash', ep.agent_secret_hash)
            print('stored_secret', 'esx_as_111b38ea568f715e58c02afba4a1bed3f0ecdf9eff3e9d')
            print('hash_of_stored_secret', sha256('esx_as_111b38ea568f715e58c02afba4a1bed3f0ecdf9eff3e9d'.encode()).hexdigest())
            print('hash_of_likely_wrong_secret', sha256('esx_as_111b38ea568f715e58c02afba4a1bed3f0ecdf9eff3e9d'.encode()).hexdigest())

asyncio.run(main())
