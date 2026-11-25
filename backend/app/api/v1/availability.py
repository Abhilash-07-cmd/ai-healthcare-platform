from fastapi import APIRouter, Depends, Request, Query, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from app.core.database import get_db
from app.schemas.availability import (
    DoctorAvailabilitySetRequest,
    DoctorAvailabilityResponse,
    DoctorLeaveCreate,
    DoctorLeaveResponse,
    SlotGenerationRequest,
    AppointmentSlotResponse
)
from app.services.availability_service import (
    set_doctor_availability,
    get_doctor_availability,
    create_doctor_leave,
    get_doctor_leaves,
    delete_doctor_leave,
    generate_doctor_slots,
    get_available_slots
)
from app.services.profile_service import get_doctor_by_user_id
from app.api.deps import RequireRole, get_current_user
from app.models.all_models import User, UserRoleEnum

router = APIRouter(prefix="/doctors", tags=["Doctor Availability & Appointment Slots"])


@router.get(
    "/me/availability",
    response_model=List[DoctorAvailabilityResponse],
    summary="Get Doctor's Own Working Hours",
    description="Retrieves the logged-in doctor's weekly working schedule rules."
)
def get_my_availability(
    current_user: User = Depends(RequireRole([UserRoleEnum.DOCTOR])),
    db: Session = Depends(get_db)
):
    doctor = get_doctor_by_user_id(db, current_user.id)
    return get_doctor_availability(db=db, doctor_id=doctor.id)


@router.post(
    "/me/availability",
    response_model=List[DoctorAvailabilityResponse],
    summary="Set Doctor's Weekly Working Schedule",
    description="Configures day-of-week working hours, shift windows, and slot durations (e.g. 30 minutes)."
)
def set_my_availability(
    request_in: DoctorAvailabilitySetRequest,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.DOCTOR])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    doctor = get_doctor_by_user_id(db, current_user.id)
    return set_doctor_availability(
        db=db,
        doctor_id=doctor.id,
        availability_items=request_in.availability,
        ip_address=ip_address
    )


@router.get(
    "/me/leave",
    response_model=List[DoctorLeaveResponse],
    summary="Get Doctor's Own Leave History",
    description="Lists all recorded leave periods and holidays for the authenticated doctor."
)
def get_my_leaves(
    current_user: User = Depends(RequireRole([UserRoleEnum.DOCTOR])),
    db: Session = Depends(get_db)
):
    doctor = get_doctor_by_user_id(db, current_user.id)
    return get_doctor_leaves(db=db, doctor_id=doctor.id)


@router.post(
    "/me/leave",
    response_model=DoctorLeaveResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Doctor Leave / Holiday",
    description="Records a leave period; appointment slot generation will automatically exclude these dates."
)
def add_my_leave(
    leave_in: DoctorLeaveCreate,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.DOCTOR])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    doctor = get_doctor_by_user_id(db, current_user.id)
    return create_doctor_leave(
        db=db,
        doctor_id=doctor.id,
        leave_in=leave_in,
        ip_address=ip_address
    )


@router.delete(
    "/me/leave/{leave_id}",
    summary="Cancel / Delete Leave Record",
    description="Removes a leave record for the doctor."
)
def remove_my_leave(
    leave_id: int,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.DOCTOR])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    doctor = get_doctor_by_user_id(db, current_user.id)
    return delete_doctor_leave(
        db=db,
        doctor_id=doctor.id,
        leave_id=leave_id,
        ip_address=ip_address
    )


@router.post(
    "/{id}/generate-slots",
    summary="Generate Appointment Slots for Doctor",
    description="Triggers automatic generation of discrete unbooked appointment slots for a specified date range."
)
def trigger_slot_generation(
    id: int,
    gen_in: SlotGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    slots_created = generate_doctor_slots(
        db=db,
        doctor_id=id,
        start_date=gen_in.start_date,
        end_date=gen_in.end_date
    )
    return {
        "message": f"Successfully generated {slots_created} new appointment slots.",
        "doctor_id": id,
        "slots_created": slots_created,
        "start_date": str(gen_in.start_date),
        "end_date": str(gen_in.end_date)
    }


@router.get(
    "/{id}/slots",
    response_model=List[AppointmentSlotResponse],
    summary="Query Available Appointment Slots",
    description="Public/Patient endpoint to retrieve available unbooked slots for a doctor on a given date."
)
def get_doctor_available_slots(
    id: int,
    target_date: date = Query(..., description="Target date for appointment (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    return get_available_slots(db=db, doctor_id=id, target_date=target_date)
