from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.schemas.queue import LiveQueueStatusResponse
from app.services.queue_service import get_live_queue_status
from app.api.deps import get_current_user
from app.models.all_models import User

router = APIRouter(prefix="/queue", tags=["Live Clinic Queue System"])


@router.get(
    "/live",
    response_model=LiveQueueStatusResponse,
    summary="Get Live Clinic Queue Status & Estimated Wait Time",
    description="Returns live queue metrics including patients ahead, currently serving queue number, and estimated waiting time."
)
def get_live_queue(
    doctor_id: int = Query(..., description="Target Doctor ID"),
    target_date: Optional[date] = Query(None, description="Date for queue (defaults to today)"),
    db: Session = Depends(get_db)
):
    return get_live_queue_status(
        db=db,
        doctor_id=doctor_id,
        target_date=target_date
    )
