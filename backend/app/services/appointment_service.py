from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status
from datetime import date, time, datetime
from typing import List, Optional

from app.models.all_models import (
    Appointment, AppointmentSlot, Patient, Doctor, Department, User, UserRoleEnum,
    AppointmentStatusEnum, AppointmentTypeEnum, Notification
)
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentReschedule
from app.services.audit_service import create_audit_log
from app.services.profile_service import get_patient_by_user_id, get_doctor_by_user_id


def book_appointment(
    db: Session,
    patient_user_id: int,
    appt_in: AppointmentCreate,
    ip_address: Optional[str] = None
) -> Appointment:
    # 1. Retrieve patient profile
    patient = get_patient_by_user_id(db, patient_user_id)

    # 2. Retrieve doctor
    doctor = db.query(Doctor).filter(Doctor.id == appt_in.doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {appt_in.doctor_id} not found."
        )

    if not doctor.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor is currently unavailable for bookings."
        )

    # 3. Prevent double booking check on existing active appointments
    existing_appt = db.query(Appointment).filter(
        Appointment.doctor_id == appt_in.doctor_id,
        Appointment.appointment_date == appt_in.appointment_date,
        Appointment.start_time == appt_in.start_time,
        Appointment.status.in_([
            AppointmentStatusEnum.REQUESTED,
            AppointmentStatusEnum.CONFIRMED,
            AppointmentStatusEnum.IN_PROGRESS
        ])
    ).first()

    if existing_appt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This appointment slot has already been booked by another patient."
        )

    # 4. Slot reservation lock
    slot = db.query(AppointmentSlot).filter(
        AppointmentSlot.doctor_id == appt_in.doctor_id,
        AppointmentSlot.slot_date == appt_in.appointment_date,
        AppointmentSlot.start_time == appt_in.start_time
    ).first()

    if slot:
        if slot.is_booked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This slot is already marked as booked."
            )
        slot.is_booked = True
    else:
        # Create slot and mark booked
        slot = AppointmentSlot(
            doctor_id=appt_in.doctor_id,
            slot_date=appt_in.appointment_date,
            start_time=appt_in.start_time,
            end_time=appt_in.end_time,
            is_booked=True
        )
        db.add(slot)

    # 5. Compute queue number for the day
    max_queue = db.query(func.max(Appointment.queue_number)).filter(
        Appointment.doctor_id == appt_in.doctor_id,
        Appointment.appointment_date == appt_in.appointment_date
    ).scalar() or 0
    next_queue = max_queue + 1

    # 6. Create Appointment
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=appt_in.doctor_id,
        department_id=appt_in.department_id,
        appointment_date=appt_in.appointment_date,
        start_time=appt_in.start_time,
        end_time=appt_in.end_time,
        appointment_type=appt_in.appointment_type,
        status=AppointmentStatusEnum.CONFIRMED,
        reason_for_visit=appt_in.reason_for_visit,
        queue_number=next_queue
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    # 7. Create notification for patient
    notif = Notification(
        user_id=patient_user_id,
        title="Appointment Confirmed",
        message=(
            f"Your appointment with Dr. {doctor.user.full_name} is confirmed for "
            f"{appointment.appointment_date} at {appointment.start_time.strftime('%H:%M')}."
        ),
        notification_type="APPOINTMENT_CONFIRMED"
    )
    db.add(notif)

    # 8. Audit log
    create_audit_log(
        db=db,
        action="BOOK_APPOINTMENT",
        resource="appointments",
        user_id=patient_user_id,
        resource_id=str(appointment.id),
        details={
            "doctor_id": doctor.id,
            "date": str(appointment.appointment_date),
            "start_time": str(appointment.start_time)
        },
        ip_address=ip_address
    )

    return get_appointment_by_id_internal(db, appointment.id)


def get_appointment_by_id_internal(db: Session, appt_id: int) -> Appointment:
    appt = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient).joinedload(Patient.user),
            joinedload(Appointment.doctor).joinedload(Doctor.user),
            joinedload(Appointment.doctor).joinedload(Doctor.department),
            joinedload(Appointment.department)
        )
        .filter(Appointment.id == appt_id)
        .first()
    )
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found."
        )
    return appt


def get_appointment_by_id(db: Session, appt_id: int, current_user: User) -> Appointment:
    appt = get_appointment_by_id_internal(db, appt_id)

    # Permission check
    if current_user.role == UserRoleEnum.PATIENT:
        if appt.patient.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this appointment."
            )
    elif current_user.role == UserRoleEnum.DOCTOR:
        if appt.doctor.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view another doctor's patient appointment."
            )

    return appt


def list_appointments(
    db: Session,
    current_user: User,
    status_filter: Optional[AppointmentStatusEnum] = None,
    date_filter: Optional[date] = None,
    doctor_id_filter: Optional[int] = None,
    patient_id_filter: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Appointment]:
    query = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient).joinedload(Patient.user),
            joinedload(Appointment.doctor).joinedload(Doctor.user),
            joinedload(Appointment.doctor).joinedload(Doctor.department),
            joinedload(Appointment.department)
        )
    )

    # Scoping rules
    if current_user.role == UserRoleEnum.PATIENT:
        patient = get_patient_by_user_id(db, current_user.id)
        query = query.filter(Appointment.patient_id == patient.id)
    elif current_user.role == UserRoleEnum.DOCTOR:
        doctor = get_doctor_by_user_id(db, current_user.id)
        query = query.filter(Appointment.doctor_id == doctor.id)

    # Additional filters
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    if date_filter:
        query = query.filter(Appointment.appointment_date == date_filter)
    if doctor_id_filter and current_user.role == UserRoleEnum.ADMIN:
        query = query.filter(Appointment.doctor_id == doctor_id_filter)
    if patient_id_filter and current_user.role == UserRoleEnum.ADMIN:
        query = query.filter(Appointment.patient_id == patient_id_filter)

    return query.order_by(Appointment.appointment_date.desc(), Appointment.start_time.asc()).offset(skip).limit(limit).all()


def update_appointment_status(
    db: Session,
    appt_id: int,
    update_in: AppointmentUpdate,
    current_user: User,
    ip_address: Optional[str] = None
) -> Appointment:
    appt = get_appointment_by_id(db, appt_id, current_user)

    # Only Doctors & Admins can update status or notes
    if current_user.role not in [UserRoleEnum.DOCTOR, UserRoleEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authorized doctors and admins can update appointment status or notes."
        )

    if update_in.status is not None:
        appt.status = update_in.status
    if update_in.notes is not None:
        appt.notes = update_in.notes
    if update_in.queue_number is not None:
        appt.queue_number = update_in.queue_number

    db.commit()
    db.refresh(appt)

    create_audit_log(
        db=db,
        action="UPDATE_APPOINTMENT",
        resource="appointments",
        user_id=current_user.id,
        resource_id=str(appt.id),
        details={"status": appt.status.value},
        ip_address=ip_address
    )

    return get_appointment_by_id_internal(db, appt_id)


def cancel_appointment(
    db: Session,
    appt_id: int,
    current_user: User,
    reason: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Appointment:
    appt = get_appointment_by_id(db, appt_id, current_user)

    if appt.status == AppointmentStatusEnum.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already cancelled."
        )

    if appt.status == AppointmentStatusEnum.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completed appointments cannot be cancelled."
        )

    # 1. Update status
    appt.status = AppointmentStatusEnum.CANCELLED
    if reason:
        appt.notes = f"{appt.notes or ''}\nCancellation Reason: {reason}".strip()

    # 2. Release slot
    slot = db.query(AppointmentSlot).filter(
        AppointmentSlot.doctor_id == appt.doctor_id,
        AppointmentSlot.slot_date == appt.appointment_date,
        AppointmentSlot.start_time == appt.start_time
    ).first()

    if slot:
        slot.is_booked = False

    db.commit()
    db.refresh(appt)

    # 3. Notification & Audit Log
    notif = Notification(
        user_id=appt.patient.user_id,
        title="Appointment Cancelled",
        message=f"Your appointment on {appt.appointment_date} at {appt.start_time} has been cancelled.",
        notification_type="APPOINTMENT_CANCELLED"
    )
    db.add(notif)

    create_audit_log(
        db=db,
        action="CANCEL_APPOINTMENT",
        resource="appointments",
        user_id=current_user.id,
        resource_id=str(appt.id),
        details={"cancelled_by": current_user.email, "reason": reason},
        ip_address=ip_address
    )

    # 4. Trigger automatic waitlist notification for freed slot
    try:
        from app.services.waitlist_service import notify_eligible_waitlisted_patients
        notify_eligible_waitlisted_patients(
            db=db,
            doctor_id=appt.doctor_id,
            department_id=appt.department_id,
            cancelled_date=appt.appointment_date
        )
    except Exception as e:
        pass

    return get_appointment_by_id_internal(db, appt_id)


def reschedule_appointment(
    db: Session,
    appt_id: int,
    resch_in: AppointmentReschedule,
    current_user: User,
    ip_address: Optional[str] = None
) -> Appointment:
    appt = get_appointment_by_id(db, appt_id, current_user)

    if appt.status in [AppointmentStatusEnum.CANCELLED, AppointmentStatusEnum.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reschedule an appointment with status {appt.status.value}."
        )

    # 1. Verify new slot availability
    existing_conflict = db.query(Appointment).filter(
        Appointment.doctor_id == appt.doctor_id,
        Appointment.appointment_date == resch_in.new_date,
        Appointment.start_time == resch_in.new_start_time,
        Appointment.status.in_([
            AppointmentStatusEnum.REQUESTED,
            AppointmentStatusEnum.CONFIRMED,
            AppointmentStatusEnum.IN_PROGRESS
        ]),
        Appointment.id != appt.id
    ).first()

    if existing_conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested new appointment slot is already booked."
        )

    # 2. Release old slot
    old_slot = db.query(AppointmentSlot).filter(
        AppointmentSlot.doctor_id == appt.doctor_id,
        AppointmentSlot.slot_date == appt.appointment_date,
        AppointmentSlot.start_time == appt.start_time
    ).first()
    if old_slot:
        old_slot.is_booked = False

    # 3. Reserve new slot
    new_slot = db.query(AppointmentSlot).filter(
        AppointmentSlot.doctor_id == appt.doctor_id,
        AppointmentSlot.slot_date == resch_in.new_date,
        AppointmentSlot.start_time == resch_in.new_start_time
    ).first()

    if new_slot:
        new_slot.is_booked = True
    else:
        new_slot = AppointmentSlot(
            doctor_id=appt.doctor_id,
            slot_date=resch_in.new_date,
            start_time=resch_in.new_start_time,
            end_time=resch_in.new_end_time,
            is_booked=True
        )
        db.add(new_slot)

    # 4. Update appointment
    old_date = appt.appointment_date
    old_time = appt.start_time
    appt.appointment_date = resch_in.new_date
    appt.start_time = resch_in.new_start_time
    appt.end_time = resch_in.new_end_time
    appt.status = AppointmentStatusEnum.CONFIRMED

    if resch_in.reason:
        appt.notes = f"{appt.notes or ''}\nRescheduled Reason: {resch_in.reason}".strip()

    db.commit()
    db.refresh(appt)

    # 5. Notification & Audit Log
    notif = Notification(
        user_id=appt.patient.user_id,
        title="Appointment Rescheduled",
        message=f"Your appointment was rescheduled to {appt.appointment_date} at {appt.start_time}.",
        notification_type="APPOINTMENT_RESCHEDULED"
    )
    db.add(notif)

    create_audit_log(
        db=db,
        action="RESCHEDULE_APPOINTMENT",
        resource="appointments",
        user_id=current_user.id,
        resource_id=str(appt.id),
        details={
            "old_date": str(old_date),
            "old_time": str(old_time),
            "new_date": str(appt.appointment_date),
            "new_time": str(appt.start_time)
        },
        ip_address=ip_address
    )

    return get_appointment_by_id_internal(db, appt_id)
