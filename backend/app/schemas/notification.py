from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    notifications: List[NotificationResponse]


class NotificationCountResponse(BaseModel):
    unread_count: int


class NotificationMarkReadRequest(BaseModel):
    notification_ids: Optional[List[int]] = Field(
        default=None,
        description="List of notification IDs to mark as read. If null or empty, marks ALL as read."
    )
