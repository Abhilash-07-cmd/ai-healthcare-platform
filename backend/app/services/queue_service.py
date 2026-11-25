from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date
from typing import Optional

from app.models.all_models import Appointment, Doctor, AppointmentStatusEnum
from app.schemas.queue import LiveQueueStatusResponse
from app.services.profile_service import get_doctor_by_id, get_patient_by_user_id


AVERAGE_CONSULTATION_MINUTES = 15


def get_live_queue_status(
    db: Session,
    doctor_id: int,
    target_date: Optional[date] = None,
    patient_user_id: Optional[int] = None
) -> LiveQueueStatusResponse:
    doctor = get_doctor_by_id(db, doctor_id)
    if not target_date:
        target_date = date.today()

    # Query today's active appointments for doctor
    active_appts = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == target_date,
            Appointment.status.in_([
                AppointmentStatusEnum.CONFIRMED,
                AppointmentStatusEnum.IN_PROGRESS
            ])
        )
        .order_by(Appointment.queue_number.asc())
        .all()
    )

    in_progress = next((a for a in active_appts if a.status == AppointmentStatusEnum.IN_PROGRESS), None)
    current_serving_q = in_progress.queue_number if in_progress else 0
    currently_serving_status = f"Queue #{current_serving_q} in Consultation" if in_progress else "Waiting for Next Patient"

    patient_q = None
    patients_ahead = 0

    if patient_user_id:
        try:
            patient = get_patient_by_user_id(db, patient_user_id)
            patient_appt = next((a for a in active_appts if a.patient_id == patient.id), None)
            if patient_appt:
                patient_q = patient_appt.queue_number
                if current_serving_q > 0:
                    patients_ahead = max(0, patient_q - current_serving_q - 1)
                else:
                    patients_ahead = max(0, patient_q - 1)
        except Exception:
            pass

    if not patient_user_id or patient_q is None:
        confirmed_count = len([a for a in active_appts if a.status == AppointmentStatusEnum.CONFIRMED])
        patients_ahead = confirmed_count

    est_wait = patients_ahead * AVERAGE_CONSULTATION_MINUTES

    return LiveQueueStatusResponse(
        doctor_id=doctor.id,
        doctor_name=doctor.user.full_name,
        department_name=doctor.department.name,
        date=target_date,
        patients_ahead=patients_ahead,
        current_serving_queue_number=current_serving_q,
        patient_queue_number=patient_q,
        estimated_waiting_time_minutes=est_wait,
        disclaimer=f"Estimated waiting time is approximate and calculated at {AVERAGE_CONSULTATION_MINUTES} minutes per patient ahead.",
        currently_serving_status=currently_serving_status
    )
