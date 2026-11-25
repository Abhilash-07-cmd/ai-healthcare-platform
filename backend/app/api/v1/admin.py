from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.user import UserResponse
from app.schemas.profile import AdminUserStatusUpdate, AdminUserRoleUpdate
from app.services.profile_service import (
    admin_list_users,
    admin_toggle_user_active,
    admin_update_user_role
)
from app.models.all_models import AuditLog, User, UserRoleEnum
from app.api.deps import RequireRole

router = APIRouter(prefix="/admin", tags=["Admin Management & Analytics"])


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Admin List Users",
    description="Lists all system users with optional role and status filters."
)
def list_system_users(
    role: Optional[UserRoleEnum] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    return admin_list_users(db=db, role=role, is_active=is_active, skip=skip, limit=limit)


@router.put(
    "/users/{id}/status",
    response_model=UserResponse,
    summary="Activate / Deactivate User Account",
    description="Enables or disables a user account's login access."
)
def update_user_status(
    id: int,
    status_in: AdminUserStatusUpdate,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return admin_toggle_user_active(
        db=db,
        target_user_id=id,
        is_active=status_in.is_active,
        admin_user_id=current_user.id,
        ip_address=ip_address
    )


@router.put(
    "/users/{id}/role",
    response_model=UserResponse,
    summary="Update User Role",
    description="Changes a user's role (PATIENT, DOCTOR, ADMIN) and initializes profile records as needed."
)
def update_user_role(
    id: int,
    role_in: AdminUserRoleUpdate,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return admin_update_user_role(
        db=db,
        target_user_id=id,
        new_role=role_in.role,
        admin_user_id=current_user.id,
        ip_address=ip_address
    )


@router.get(
    "/audit-logs",
    summary="View System Audit Logs",
    description="Returns recorded audit logs for administrative security monitoring."
)
def list_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    return query.order_by(AuditLog.id.desc()).offset(skip).limit(limit).all()
