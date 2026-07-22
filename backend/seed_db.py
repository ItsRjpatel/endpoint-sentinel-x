import asyncio
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.models.organization import Organization
from app.db.models.user import User
from app.db.models.enrollment_token import EnrollmentToken
from app.core.security import get_password_hash
import uuid

async def seed_db():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        from sqlalchemy import select
        # Check org
        result = await session.execute(select(Organization).filter_by(name="Test Org"))
        org = result.scalar_one_or_none()
        if not org:
            org = Organization(name="Test Org", slug="test-org")
            session.add(org)
            await session.flush()
        
        # Check user
        result = await session.execute(select(User).filter_by(email="admin@example.com"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                email="admin@example.com",
                username="admin",
                first_name="Admin",
                last_name="User",
                password_hash=get_password_hash("admin123"),
                is_active=True,
                role="SUPER_ADMIN",
                organization_id=org.id
            )
            session.add(admin)
        
        # Check token
        result = await session.execute(select(EnrollmentToken).filter_by(organization_id=org.id))
        token = result.scalars().first()
        if not token:
            token_uuid = uuid.uuid4()
            token = EnrollmentToken(
                token_value=str(token_uuid),
                organization_id=org.id,
                expires_at=datetime.now(UTC) + timedelta(days=365)
            )
            session.add(token)
        
        await session.commit()
        
        print(f"Token created/found: {token.token_value}")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_db())
