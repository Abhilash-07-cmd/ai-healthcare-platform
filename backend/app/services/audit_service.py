from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.all_models import AuditLog
from app.core.logging import logger

def create_audit_log(
    db: Session,
    action: str,
    resource: str,
    user_id: Optional[int] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Creates and commits an immutable audit log record.
    """
    try:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=str(resource_id) if resource_id is not None else None,
            details_json=details,
            ip_address=ip_address
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to record audit log: {str(e)}")
        # Do not raise exception to avoid blocking primary business operation
        return None
