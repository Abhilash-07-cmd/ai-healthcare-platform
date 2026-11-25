from fastapi import APIRouter, Depends, Request, Query, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from app.core.database import get_db
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentReschedule,
    AppointmentResponse
)
from app.services.appointment_service import (
    book_appointment,
    list_appointments,
    get_appointment_by_id,
    update_appointment_status,
    cancel_appointment,
    reschedule_appointment
)
from app.models.all_models import User, UserRoleEnum, AppointmentStatusEnum
from app.api.deps import get_current_user

router = APIRouter(prefix="/appointments", tags=["Appointments Management"])


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Book an Appointment",
    description="Reserves an appointment slot for a doctor and department. Enforces double booking prevention."
)
def create_appointment(
    appt_in: AppointmentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return book_appointment(
        db=db,
        patient_user_id=current_user.id,
        appt_in=appt_in,
        ip_address=ip_address
    )


@router.get(
    "",
    response_model=List[AppointmentResponse],
    summary="List Appointments",
    description="Returns appointment records. Automatically scoped by role (Patients see their bookings, Doctors see their schedule, Admins view system-wide)."
)
def get_appointments(
    status_filter: Optional[AppointmentStatusEnum] = Query(None, description="Filter by status"),
    date_filter: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    doctor_id: Optional[int] = Query(None, description="Admin filter by Doctor ID"),
    patient_id: Optional[int] = Query(None, description="Admin filter by Patient ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return list_appointments(
        db=db,
        current_user=current_user,
        status_filter=status_filter,
        date_filter=date_filter,
        doctor_id_filter=doctor_id,
        patient_id_filter=patient_id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{id}",
    response_model=AppointmentResponse,
    summary="Get Appointment Details",
    description="Retrieves full metadata for a specific appointment."
)
def get_appointment(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_appointment_by_id(db=db, appt_id=id, current_user=current_user)


@router.put(
    "/{id}",
    response_model=AppointmentResponse,
    summary="Update Appointment Status & Notes (Doctor / Admin)",
    description="Modifies status (e.g. IN_PROGRESS, COMPLETED, NO_SHOW) and adds clinical doctor notes."
)
def update_appointment(
    id: int,
    update_in: AppointmentUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return update_appointment_status(
        db=db,
        appt_id=id,
        update_in=update_in,
        current_user=current_user,
        ip_address=ip_address
    )


@router.post(
    "/{id}/cancel",
    response_model=AppointmentResponse,
    summary="Cancel Appointment",
    description="Cancels an appointment, releases the reserved slot (is_booked=False), and sends notification."
)
def cancel_existing_appointment(
    id: int,
    request: Request,
    reason: Optional[str] = Query(None, description="Optional cancellation reason"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return cancel_appointment(
        db=db,
        appt_id=id,
        current_user=current_user,
        reason=reason,
        ip_address=ip_address
    )


@router.post(
    "/{id}/reschedule",
    response_model=AppointmentResponse,
    summary="Reschedule Appointment",
    description="Atomically transfers an appointment to a new date and time slot, releasing the old slot."
)
def reschedule_existing_appointment(
    id: int,
    resch_in: AppointmentReschedule,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return reschedule_appointment(
        db=db,
        appt_id=id,
        resch_in=resch_in,
        current_user=current_user,
        ip_address=ip_address
    )
