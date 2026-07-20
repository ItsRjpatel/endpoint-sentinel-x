import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.health import HealthCheckResponse

router = APIRouter()
logger = structlog.get_logger()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform a system status check",
)
async def check_health(db: AsyncSession = Depends(get_db)):
    """Verifies that the API service is running, and validates connectivity
    to the underlying PostgreSQL database cluster.
    """
    services_status = {"database": "unhealthy"}
    overall_status = "healthy"

    try:
        # Ping the database
        await db.execute(text("SELECT 1"))
        services_status["database"] = "healthy"
    except Exception as e:
        logger.error("Healthcheck database connection failed", error=str(e))
        services_status["database"] = "unhealthy"
        overall_status = "unhealthy"

    # Redis health integration placeholder
    services_status["redis"] = "configured"

    response = HealthCheckResponse(status=overall_status, version="0.1.0", services=services_status)

    if overall_status == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=response.model_dump()
        )

    return response
