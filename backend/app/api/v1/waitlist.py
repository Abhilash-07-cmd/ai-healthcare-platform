from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.waitlist import WaitlistCreate, WaitlistResponse, WaitlistAcceptRequest
from app.services.waitlist_service import (
    join_waitlist,
    get_patient_waitlists,
    cancel_waitlist_entry,
    accept_waitlist_slot
)
from app.api.deps import get_current_user, RequireRole
from app.models.all_models import User, UserRoleEnum

router = APIRouter(prefix="/waitlist", tags=["Smart Waitlist"])


@router.post(
    "",
    response_model=WaitlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Join Department/Doctor Waitlist",
    description="Registers a patient on the waiting list when preferred appointment slots are fully booked."
)
def create_waitlist_entry(
    waitlist_in: WaitlistCreate,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.PATIENT])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return join_waitlist(
        db=db,
        patient_user_id=current_user.id,
        waitlist_in=waitlist_in,
        ip_address=ip_address
    )


@router.get(
    "/me",
    response_model=List[WaitlistResponse],
    summary="Get Patient's Waitlist Entries",
    description="Retrieves current active waitlist positions and statuses for the logged-in patient."
)
def get_my_waitlist(
    current_user: User = Depends(RequireRole([UserRoleEnum.PATIENT])),
    db: Session = Depends(get_db)
):
    return get_patient_waitlists(db=db, patient_user_id=current_user.id)


@router.delete(
    "/{id}",
    summary="Cancel Waitlist Entry",
    description="Removes patient from the waitlist."
)
def delete_waitlist(
    id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return cancel_waitlist_entry(
        db=db,
        waitlist_id=id,
        current_user=current_user,
        ip_address=ip_address
    )


@router.post(
    "/{id}/accept",
    summary="Accept Waitlist Slot Offer",
    description="Converts a waitlisted entry into a confirmed appointment after receiving a slot notification."
)
def accept_slot(
    id: int,
    accept_in: WaitlistAcceptRequest,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.PATIENT])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return accept_waitlist_slot(
        db=db,
        waitlist_id=id,
        accept_in=accept_in,
        current_user=current_user,
        ip_address=ip_address
    )
