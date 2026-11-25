from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status
from datetime import date, datetime
from typing import List, Optional

from app.models.all_models import (
    Waitlist, Patient, Department, Doctor, User, WaitlistStatusEnum,
    Notification, Appointment
)
from app.schemas.waitlist import WaitlistCreate, WaitlistAcceptRequest
from app.schemas.appointment import AppointmentCreate
from app.services.audit_service import create_audit_log
from app.services.profile_service import get_patient_by_user_id


def join_waitlist(
    db: Session,
    patient_user_id: int,
    waitlist_in: WaitlistCreate,
    ip_address: Optional[str] = None
) -> Waitlist:
    patient = get_patient_by_user_id(db, patient_user_id)

    # Check duplicate waiting entry
    existing = db.query(Waitlist).filter(
        Waitlist.patient_id == patient.id,
        Waitlist.department_id == waitlist_in.department_id,
        Waitlist.preferred_date == waitlist_in.preferred_date,
        Waitlist.status == WaitlistStatusEnum.WAITING
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are already on the waitlist for this date (Position #{existing.position})."
        )

    # Calculate position
    current_count = db.query(Waitlist).filter(
        Waitlist.department_id == waitlist_in.department_id,
        Waitlist.preferred_date == waitlist_in.preferred_date,
        Waitlist.status == WaitlistStatusEnum.WAITING
    ).count()

    position = current_count + 1

    entry = Waitlist(
        patient_id=patient.id,
        doctor_id=waitlist_in.doctor_id,
        department_id=waitlist_in.department_id,
        preferred_date=waitlist_in.preferred_date,
        preferred_time_slot=waitlist_in.preferred_time_slot,
        position=position,
        status=WaitlistStatusEnum.WAITING
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Notification
    notif = Notification(
        user_id=patient_user_id,
        title="Joined Waitlist",
        message=f"You are successfully added to the waitlist for {entry.preferred_date}. Your position is #{position}.",
        notification_type="WAITLIST_JOINED"
    )
    db.add(notif)

    create_audit_log(
        db=db,
        action="JOIN_WAITLIST",
        resource="waitlists",
        user_id=patient_user_id,
        resource_id=str(entry.id),
        details={"position": position, "date": str(entry.preferred_date)},
        ip_address=ip_address
    )

    return get_waitlist_by_id_internal(db, entry.id)


def get_waitlist_by_id_internal(db: Session, waitlist_id: int) -> Waitlist:
    entry = (
        db.query(Waitlist)
        .options(joinedload(Waitlist.department))
        .filter(Waitlist.id == waitlist_id)
        .first()
    )
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waitlist entry not found."
        )
    return entry


def get_patient_waitlists(db: Session, patient_user_id: int) -> List[Waitlist]:
    patient = get_patient_by_user_id(db, patient_user_id)
    return (
        db.query(Waitlist)
        .options(joinedload(Waitlist.department))
        .filter(Waitlist.patient_id == patient.id)
        .order_by(Waitlist.created_at.desc())
        .all()
    )


def cancel_waitlist_entry(db: Session, waitlist_id: int, current_user: User, ip_address: Optional[str] = None) -> dict:
    patient = get_patient_by_user_id(db, current_user.id)
    entry = get_waitlist_by_id_internal(db, waitlist_id)

    if entry.patient_id != patient.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to cancel this waitlist entry."
        )

    entry.status = WaitlistStatusEnum.CANCELLED
    db.commit()

    create_audit_log(
        db=db,
        action="CANCEL_WAITLIST",
        resource="waitlists",
        user_id=current_user.id,
        resource_id=str(waitlist_id),
        details={"status": "CANCELLED"},
        ip_address=ip_address
    )

    return {"message": "Waitlist entry cancelled successfully."}


def notify_eligible_waitlisted_patients(
    db: Session,
    doctor_id: int,
    department_id: int,
    cancelled_date: date
) -> int:
    """
    Automated trigger when an appointment is cancelled.
    Identifies top waitlisted patients and sends slot offer notifications.
    """
    eligible_entries = (
        db.query(Waitlist)
        .filter(
            Waitlist.department_id == department_id,
            Waitlist.preferred_date == cancelled_date,
            Waitlist.status == WaitlistStatusEnum.WAITING
        )
        .order_by(Waitlist.position.asc())
        .limit(3)
        .all()
    )

    notified_count = 0
    for entry in eligible_entries:
        entry.status = WaitlistStatusEnum.NOTIFIED
        patient_user_id = entry.patient.user_id
        
        notif = Notification(
            user_id=patient_user_id,
            title="Freed Appointment Slot Available!",
            message=(
                f"A slot opened up for your waitlist request on {cancelled_date}! "
                f"Log in now to accept and confirm your appointment."
            ),
            notification_type="WAITLIST_SLOT_AVAILABLE"
        )
        db.add(notif)
        notified_count += 1

    db.commit()
    return notified_count


def accept_waitlist_slot(
    db: Session,
    waitlist_id: int,
    accept_in: WaitlistAcceptRequest,
    current_user: User,
    ip_address: Optional[str] = None
) -> dict:
    from app.services.appointment_service import book_appointment

    patient = get_patient_by_user_id(db, current_user.id)
    entry = get_waitlist_by_id_internal(db, waitlist_id)

    if entry.patient_id != patient.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to accept this waitlist entry."
        )

    if entry.status not in [WaitlistStatusEnum.WAITING, WaitlistStatusEnum.NOTIFIED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept waitlist entry with status '{entry.status.value}'."
        )

    # Determine doctor ID
    doctor_id = entry.doctor_id
    if not doctor_id:
        # Pick available doctor in department
        first_doc = db.query(Doctor).filter(Doctor.department_id == entry.department_id, Doctor.is_available == True).first()
        if not first_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available doctor found in this department for booking."
            )
        doctor_id = first_doc.id

    # Create appointment
    appt_in = AppointmentCreate(
        doctor_id=doctor_id,
        department_id=entry.department_id,
        appointment_date=entry.preferred_date,
        start_time=accept_in.start_time,
        end_time=accept_in.end_time,
        reason_for_visit=f"Waitlist conversion from position #{entry.position}"
    )

    appointment = book_appointment(
        db=db,
        patient_user_id=current_user.id,
        appt_in=appt_in,
        ip_address=ip_address
    )

    # Update waitlist status
    entry.status = WaitlistStatusEnum.BOOKED
    db.commit()

    return {
        "message": "Waitlist slot successfully accepted and converted to appointment!",
        "appointment_id": appointment.id,
        "appointment_date": str(appointment.appointment_date),
        "start_time": str(appointment.start_time)
    }
