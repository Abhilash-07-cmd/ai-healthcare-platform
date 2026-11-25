from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.api.deps import RequireRole
from app.models.all_models import User, UserRoleEnum, AuditLog
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    details_json: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


router = APIRouter(prefix="/audit", tags=["Audit Logs & Security"])


@router.get(
    "",
    response_model=list[AuditLogResponse],
    summary="View Audit Logs (Admin Only)",
    description="Returns paginated audit logs of all mutating API calls. Admin only."
)
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query(None, description="Filter by HTTP method (POST, PUT, DELETE)"),
    resource: Optional[str] = Query(None, description="Filter by resource name"),
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action.upper())
    if resource:
        q = q.filter(AuditLog.resource.ilike(f"%{resource}%"))
    return q.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()


@router.get(
    "/stats",
    summary="Audit Log Stats (Admin Only)",
    description="Returns counts of audit log actions. Admin only."
)
def audit_stats(
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    from sqlalchemy import func
    results = (
        db.query(AuditLog.action, func.count(AuditLog.id).label("count"))
        .group_by(AuditLog.action)
        .all()
    )
    return {"action_counts": {r.action: r.count for r in results}}
