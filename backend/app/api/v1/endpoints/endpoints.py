from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.endpoint import EndpointListResponse, EndpointDetailsResponse
from app.services.endpoint import EndpointService

router = APIRouter(prefix="/endpoints", dependencies=[Depends(get_current_user)])


@router.get("", response_model=EndpointListResponse)
async def list_endpoints(
    db: Annotated[AsyncSession, Depends(get_db)],
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
):
    service = EndpointService(db)
    offset = (page - 1) * page_size
    return await service.list_endpoints(search=search, status=status, limit=page_size, offset=offset)


@router.get("/{endpoint_uuid}", response_model=EndpointDetailsResponse)
async def get_endpoint_details(
    endpoint_uuid: str, db: Annotated[AsyncSession, Depends(get_db)]
):
    service = EndpointService(db)
    try:
        return await service.get_endpoint_details(endpoint_uuid)
    except ValueError:
        raise HTTPException(status_code=404, detail="Endpoint not found")
