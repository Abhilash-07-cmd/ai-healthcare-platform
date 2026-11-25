from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.notification import (
    NotificationListResponse,
    NotificationCountResponse,
    NotificationMarkReadRequest
)
from app.services.notification_service import (
    get_user_notifications,
    get_unread_count,
    mark_notifications_read,
    delete_notification,
    clear_read_notifications
)
from app.api.deps import get_current_user
from app.models.all_models import User

router = APIRouter(prefix="/notifications", tags=["Notification Center"])


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List User Notifications",
    description="Returns paginated list of in-app notifications with total and unread counts."
)
def list_notifications(
    unread_only: bool = Query(False, description="Filter to show only unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_notifications(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )


@router.get(
    "/count",
    response_model=NotificationCountResponse,
    summary="Get Unread Notification Badge Count",
    description="Returns the number of unread notifications. Used for sidebar badge indicator."
)
def notification_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_unread_count(db=db, user_id=current_user.id)


@router.put(
    "/read",
    summary="Mark Specific Notifications as Read",
    description="Marks the specified notification IDs as read. Pass empty list to mark ALL as read."
)
def mark_read(
    request: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return mark_notifications_read(
        db=db,
        user_id=current_user.id,
        notification_ids=request.notification_ids
    )


@router.put(
    "/read-all",
    summary="Mark ALL Notifications as Read",
    description="Marks every unread notification for the current user as read."
)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return mark_notifications_read(
        db=db,
        user_id=current_user.id,
        notification_ids=None
    )


@router.delete(
    "/clear-read",
    summary="Clear All Read Notifications",
    description="Bulk deletes all read notifications to keep the notification center clean."
)
def clear_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return clear_read_notifications(db=db, user_id=current_user.id)


@router.delete(
    "/{notification_id}",
    summary="Delete Single Notification",
    description="Permanently deletes a specific notification by ID."
)
def delete_single_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_notification(
        db=db,
        user_id=current_user.id,
        notification_id=notification_id
    )
