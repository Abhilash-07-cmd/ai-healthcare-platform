from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date, time, datetime, timedelta
from typing import List, Optional

from app.models.all_models import Doctor, DoctorAvailability, DoctorLeave, AppointmentSlot
from app.schemas.availability import DoctorAvailabilityItem, DoctorLeaveCreate
from app.services.audit_service import create_audit_log
from app.services.profile_service import get_doctor_by_user_id, get_doctor_by_id


def set_doctor_availability(
    db: Session,
    doctor_id: int,
    availability_items: List[DoctorAvailabilityItem],
    ip_address: Optional[str] = None
) -> List[DoctorAvailability]:
    # Validate doctor exists
    doctor = get_doctor_by_id(db, doctor_id)

    # Delete existing availability configuration for doctor
    db.query(DoctorAvailability).filter(DoctorAvailability.doctor_id == doctor_id).delete()

    new_records = []
    for item in availability_items:
        if item.end_time <= item.start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"End time {item.end_time} must be strictly after start time {item.start_time} for day {item.day_of_week}."
            )
        avail = DoctorAvailability(
            doctor_id=doctor_id,
            day_of_week=item.day_of_week,
            start_time=item.start_time,
            end_time=item.end_time,
            slot_duration_minutes=item.slot_duration_minutes
        )
        db.add(avail)
        new_records.append(avail)

    db.commit()

    create_audit_log(
        db=db,
        action="UPDATE_DOCTOR_AVAILABILITY",
        resource="doctor_availability",
        user_id=doctor.user_id,
        resource_id=str(doctor_id),
        details={"record_count": len(new_records)},
        ip_address=ip_address
    )

    return get_doctor_availability(db, doctor_id)


def get_doctor_availability(db: Session, doctor_id: int) -> List[DoctorAvailability]:
    return (
        db.query(DoctorAvailability)
        .filter(DoctorAvailability.doctor_id == doctor_id)
        .order_by(DoctorAvailability.day_of_week.asc(), DoctorAvailability.start_time.asc())
        .all()
    )


def create_doctor_leave(
    db: Session,
    doctor_id: int,
    leave_in: DoctorLeaveCreate,
    ip_address: Optional[str] = None
) -> DoctorLeave:
    if leave_in.end_date < leave_in.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave end date cannot be earlier than start date."
        )

    doctor = get_doctor_by_id(db, doctor_id)

    leave = DoctorLeave(
        doctor_id=doctor_id,
        start_date=leave_in.start_date,
        end_date=leave_in.end_date,
        reason=leave_in.reason,
        status="APPROVED"
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)

    create_audit_log(
        db=db,
        action="CREATE_DOCTOR_LEAVE",
        resource="doctor_leave",
        user_id=doctor.user_id,
        resource_id=str(leave.id),
        details={"start_date": str(leave.start_date), "end_date": str(leave.end_date)},
        ip_address=ip_address
    )

    return leave


def get_doctor_leaves(db: Session, doctor_id: int) -> List[DoctorLeave]:
    return (
        db.query(DoctorLeave)
        .filter(DoctorLeave.doctor_id == doctor_id)
        .order_by(DoctorLeave.start_date.desc())
        .all()
    )


def delete_doctor_leave(db: Session, doctor_id: int, leave_id: int, ip_address: Optional[str] = None) -> dict:
    leave = db.query(DoctorLeave).filter(
        DoctorLeave.id == leave_id,
        DoctorLeave.doctor_id == doctor_id
    ).first()

    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave record not found."
        )

    db.delete(leave)
    db.commit()
    return {"message": "Leave record deleted successfully."}


def generate_doctor_slots(
    db: Session,
    doctor_id: int,
    start_date: date,
    end_date: date
) -> int:
    """
    Generates discrete 30-minute appointment slots for the doctor across requested date range,
    skipping dates where the doctor is on approved leave.
    """
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be on or after start date."
        )

    # Max window limit (e.g. 30 days max per batch)
    if (end_date - start_date).days > 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot generation range cannot exceed 60 days in a single request."
        )

    availabilities = get_doctor_availability(db, doctor_id)
    if not availabilities:
        # Provide fallback default availability (Mon-Fri 09:00-17:00, 30m slots) if none configured
        for day in range(5):  # Mon-Fri
            default_avail = DoctorAvailability(
                doctor_id=doctor_id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                slot_duration_minutes=30
            )
            db.add(default_avail)
        db.commit()
        availabilities = get_doctor_availability(db, doctor_id)

    leaves = get_doctor_leaves(db, doctor_id)

    # Helper to check leave
    def is_on_leave(target_dt: date) -> bool:
        for l in leaves:
            if l.start_date <= target_dt <= l.end_date:
                return True
        return False

    slots_created = 0
    current_dt = start_date

    while current_dt <= end_date:
        if not is_on_leave(current_dt):
            weekday = current_dt.weekday()  # 0=Mon, 6=Sun
            day_avails = [a for a in availabilities if a.day_of_week == weekday]

            for avail in day_avails:
                slot_delta = timedelta(minutes=avail.slot_duration_minutes)
                start_dt_time = datetime.combine(current_dt, avail.start_time)
                end_dt_time = datetime.combine(current_dt, avail.end_time)

                current_slot_start = start_dt_time
                while current_slot_start + slot_delta <= end_dt_time:
                    slot_start_t = current_slot_start.time()
                    slot_end_t = (current_slot_start + slot_delta).time()

                    # Check if slot already exists
                    existing = db.query(AppointmentSlot).filter(
                        AppointmentSlot.doctor_id == doctor_id,
                        AppointmentSlot.slot_date == current_dt,
                        AppointmentSlot.start_time == slot_start_t
                    ).first()

                    if not existing:
                        new_slot = AppointmentSlot(
                            doctor_id=doctor_id,
                            slot_date=current_dt,
                            start_time=slot_start_t,
                            end_time=slot_end_t,
                            is_booked=False
                        )
                        db.add(new_slot)
                        slots_created += 1

                    current_slot_start += slot_delta

        current_dt += timedelta(days=1)

    db.commit()
    return slots_created


def get_available_slots(
    db: Session,
    doctor_id: int,
    target_date: date
) -> List[AppointmentSlot]:
    """
    Returns unbooked appointment slots for a doctor on a specific date.
    If no slots exist yet for the target date, triggers slot generation automatically.
    """
    slots = (
        db.query(AppointmentSlot)
        .filter(
            AppointmentSlot.doctor_id == doctor_id,
            AppointmentSlot.slot_date == target_date,
            AppointmentSlot.is_booked == False
        )
        .order_by(AppointmentSlot.start_time.asc())
        .all()
    )

    if not slots:
        # Auto-generate slots for target date if none exist
        generate_doctor_slots(db, doctor_id=doctor_id, start_date=target_date, end_date=target_date)
        slots = (
            db.query(AppointmentSlot)
            .filter(
                AppointmentSlot.doctor_id == doctor_id,
                AppointmentSlot.slot_date == target_date,
                AppointmentSlot.is_booked == False
            )
            .order_by(AppointmentSlot.start_time.asc())
            .all()
        )

    return slots
