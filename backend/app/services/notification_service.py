from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.all_models import Notification
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationCountResponse
)


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "GENERAL"
) -> Notification:
    """Internal helper used by all services to create a notification."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        is_read=False
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def get_user_notifications(
    db: Session,
    user_id: int,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0
) -> NotificationListResponse:
    query = db.query(Notification).filter(Notification.user_id == user_id)

    total = query.count()
    unread_count = query.filter(Notification.is_read == False).count()

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = (
        query.order_by(desc(Notification.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return NotificationListResponse(
        total=total,
        unread_count=unread_count,
        notifications=[NotificationResponse.model_validate(n) for n in notifications]
    )


def get_unread_count(db: Session, user_id: int) -> NotificationCountResponse:
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()
    return NotificationCountResponse(unread_count=count)


def mark_notifications_read(
    db: Session,
    user_id: int,
    notification_ids: Optional[List[int]] = None
) -> dict:
    """Mark specific notifications or ALL as read."""
    query = db.query(Notification).filter(Notification.user_id == user_id)

    if notification_ids:
        query = query.filter(Notification.id.in_(notification_ids))

    updated = query.filter(Notification.is_read == False).all()
    count = len(updated)

    for notif in updated:
        notif.is_read = True

    db.commit()
    return {"message": f"{count} notification(s) marked as read.", "updated_count": count}


def delete_notification(
    db: Session,
    user_id: int,
    notification_id: int
) -> dict:
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found."
        )

    db.delete(notif)
    db.commit()
    return {"message": "Notification deleted successfully."}


def clear_read_notifications(db: Session, user_id: int) -> dict:
    """Bulk delete all read notifications for the user."""
    read_notifs = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == True
    ).all()

    count = len(read_notifs)
    for n in read_notifs:
        db.delete(n)

    db.commit()
    return {"message": f"{count} read notification(s) cleared.", "deleted_count": count}
