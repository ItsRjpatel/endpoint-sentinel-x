import asyncio
from sqlalchemy import func, select
from app.db.models.performance_history import PerformanceHistory
from app.db.session import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(PerformanceHistory).order_by(PerformanceHistory.timestamp.desc()).limit(5))).scalars().all()
        print('rows_for_endpoint', len(rows))
        for row in rows:
            print(row.id, row.endpoint_id, row.timestamp, row.cpu_usage_percent, row.memory_usage_percent, row.disk_usage_percent, row.network_in_bytes, row.network_out_bytes)

asyncio.run(main())
