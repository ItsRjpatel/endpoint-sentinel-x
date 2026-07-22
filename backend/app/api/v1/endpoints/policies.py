from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.policy import Policy
from app.db.models.user import User
from app.dependencies.auth import get_current_active_user, require_org_admin
from app.dependencies.database import get_db
from app.schemas.policy import (
    PolicyAssignmentCreate,
    PolicyAssignmentResponse,
    PolicyCreate,
    PolicyListResponse,
    PolicyResponse,
    PolicyUpdate,
)
from app.services.policy import PolicyService

router = APIRouter(prefix="/policies", dependencies=[Depends(get_current_active_user)])


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_in: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_org_admin),
) -> Policy:
    """Create a new policy (Organization Admin only)."""
    service = PolicyService(db)
    policy = await service.create_policy(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        policy_in=policy_in,
    )
    await db.commit()
    return policy


@router.get("", response_model=list[PolicyListResponse])
async def list_policies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Sequence[Policy]:
    """List all policies for the current user's organization."""
    service = PolicyService(db)
    return await service.list_policies(current_user.organization_id)


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Policy:
    """Get policy details including versions and assignments."""
    service = PolicyService(db)
    policy = await service.get_policy(policy_id)
    if not policy or policy.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: int,
    policy_in: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_org_admin),
) -> Policy:
    """Update a policy and optionally create a new version (Organization Admin only)."""
    service = PolicyService(db)
    policy = await service.get_policy(policy_id)
    if not policy or policy.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    updated = await service.update_policy(policy_id, policy_in)
    await db.commit()
    return updated


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_org_admin),
) -> None:
    """Delete a policy (Organization Admin only)."""
    service = PolicyService(db)
    policy = await service.get_policy(policy_id)
    if not policy or policy.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    await service.delete_policy(policy_id)
    await db.commit()


@router.post("/{policy_id}/assign", response_model=PolicyAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_policy(
    policy_id: int,
    assignment_in: PolicyAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_org_admin),
):
    """Assign a policy to an endpoint."""
    service = PolicyService(db)
    policy = await service.get_policy(policy_id)
    if not policy or policy.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    assignment = await service.assign_endpoint(
        policy_id=policy_id,
        endpoint_id=assignment_in.endpoint_id,
        user_id=current_user.id
    )
    if not assignment:
        raise HTTPException(status_code=400, detail="Failed to assign policy")
        
    await db.commit()
    return assignment


@router.delete("/{policy_id}/assign/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_policy(
    policy_id: int,
    endpoint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_org_admin),
) -> None:
    """Remove a policy assignment from an endpoint."""
    service = PolicyService(db)
    policy = await service.get_policy(policy_id)
    if not policy or policy.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    success = await service.unassign_endpoint(policy_id, endpoint_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    await db.commit()
