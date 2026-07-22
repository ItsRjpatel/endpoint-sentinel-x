import asyncio
import httpx
from sqlalchemy import select
from app.db.models.endpoint import Endpoint
from app.db.session import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        ep = (await db.execute(select(Endpoint).where(Endpoint.agent_id == 'bde173ad-adee-4b86-8867-ce9faf02fc03'))).scalar_one_or_none()
        print('endpoint', ep.id if ep else None)
        print('hash', ep.agent_secret_hash if ep else None)

    payload = {"status": "healthy", "cpu_pct": 42.5, "ram_pct": 61.2, "disk_pct": 18.9, "network_in": 12345, "network_out": 6789}
    headers = {
        'X-Agent-ID': 'bde173ad-adee-4b86-8867-ce9faf02fc03',
        'X-Agent-Secret': 'esx_as_f26fdcf2c6c6a99cd6ec24198cd97ab0c5f1b653546db046cae3a649a1b12d79',
        'Content-Type': 'application/json',
    }
    with httpx.Client() as client:
        r = client.post('http://127.0.0.1:8000/api/v1/agent/heartbeat', json=payload, headers=headers)
        print('status', r.status_code)
        print(r.text)

asyncio.run(main())
