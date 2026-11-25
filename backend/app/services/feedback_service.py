import logging
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.all_models import (
    Feedback, Appointment, Doctor, Patient, User,
    AppointmentStatusEnum, UserRoleEnum
)
from app.schemas.feedback import (
    FeedbackCreateRequest, FeedbackResponse,
    FeedbackListResponse, DoctorRatingSummary
)

logger = logging.getLogger("healthcare_platform.feedback_service")


def _build_feedback_response(fb: Feedback, db: Session) -> FeedbackResponse:
    """Enrich a Feedback ORM object with doctor/patient names."""
    doctor_name = None
    patient_name = None

    if fb.appointment_id:
        appt = db.query(Appointment).filter(Appointment.id == fb.appointment_id).first()
        if appt:
            doc = db.query(Doctor).filter(Doctor.id == appt.doctor_id).first()
            if doc:
                doctor_name = doc.user.full_name
            patient = db.query(Patient).filter(Patient.id == appt.patient_id).first()
            if patient:
                patient_name = patient.user.full_name

    return FeedbackResponse(
        id=fb.id,
        appointment_id=fb.appointment_id,
        rating=fb.rating,
        comments=fb.comments,
        created_at=fb.created_at,
        doctor_name=doctor_name,
        patient_name=patient_name
    )


def submit_feedback(
    db: Session, user: User, payload: FeedbackCreateRequest
) -> FeedbackResponse:
    # Fetch the appointment
    appt = db.query(Appointment).filter(Appointment.id == payload.appointment_id).first()
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found."
        )

    # Only the patient of the appointment can leave feedback
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    if not patient or appt.patient_id != patient.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review your own appointments."
        )

    # Appointment must be COMPLETED
    if appt.status != AppointmentStatusEnum.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback can only be submitted for completed appointments."
        )

    # Prevent duplicate feedback for same appointment
    existing = db.query(Feedback).filter(
        Feedback.appointment_id == payload.appointment_id,
        Feedback.user_id == user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already submitted feedback for this appointment."
        )

    fb = Feedback(
        user_id=user.id,
        appointment_id=payload.appointment_id,
        rating=payload.rating,
        comments=payload.comments
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    # Recalculate and update the doctor's aggregate rating
    _recalculate_doctor_rating(db, appt.doctor_id)

    logger.info(f"Feedback submitted: user_id={user.id}, appt_id={payload.appointment_id}, rating={payload.rating}")
    return _build_feedback_response(fb, db)


def _recalculate_doctor_rating(db: Session, doctor_id: int) -> None:
    """Recompute and persist the doctor's average rating from all feedback."""
    feedbacks = (
        db.query(Feedback)
        .join(Appointment, Appointment.id == Feedback.appointment_id)
        .filter(Appointment.doctor_id == doctor_id)
        .all()
    )
    if not feedbacks:
        return

    avg = sum(f.rating for f in feedbacks) / len(feedbacks)
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doc:
        doc.rating = round(avg, 2)
        db.commit()


def get_my_feedbacks(db: Session, user: User) -> FeedbackListResponse:
    feedbacks = (
        db.query(Feedback)
        .filter(Feedback.user_id == user.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    avg = round(sum(f.rating for f in feedbacks) / len(feedbacks), 2) if feedbacks else 0.0
    return FeedbackListResponse(
        total=len(feedbacks),
        average_rating=avg,
        feedbacks=[_build_feedback_response(f, db) for f in feedbacks]
    )


def get_doctor_feedbacks(db: Session, doctor_id: int) -> FeedbackListResponse:
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

    feedbacks = (
        db.query(Feedback)
        .join(Appointment, Appointment.id == Feedback.appointment_id)
        .filter(Appointment.doctor_id == doctor_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    avg = round(sum(f.rating for f in feedbacks) / len(feedbacks), 2) if feedbacks else 0.0
    return FeedbackListResponse(
        total=len(feedbacks),
        average_rating=avg,
        feedbacks=[_build_feedback_response(f, db) for f in feedbacks]
    )


def get_doctor_rating_summary(db: Session, doctor_id: int) -> DoctorRatingSummary:
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

    feedbacks = (
        db.query(Feedback)
        .join(Appointment, Appointment.id == Feedback.appointment_id)
        .filter(Appointment.doctor_id == doctor_id)
        .all()
    )

    breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for f in feedbacks:
        breakdown[f.rating] = breakdown.get(f.rating, 0) + 1

    avg = round(sum(f.rating for f in feedbacks) / len(feedbacks), 2) if feedbacks else 0.0

    return DoctorRatingSummary(
        doctor_id=doc.id,
        doctor_name=doc.user.full_name,
        department=doc.department.name,
        total_reviews=len(feedbacks),
        average_rating=avg,
        rating_breakdown=breakdown
    )


def delete_feedback(db: Session, user: User, feedback_id: int) -> dict:
    """Admin-only: remove a review."""
    if user.role != UserRoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only.")

    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found.")

    appt = db.query(Appointment).filter(Appointment.id == fb.appointment_id).first()
    doctor_id = appt.doctor_id if appt else None

    db.delete(fb)
    db.commit()

    if doctor_id:
        _recalculate_doctor_rating(db, doctor_id)

    return {"message": f"Feedback #{feedback_id} deleted successfully."}
