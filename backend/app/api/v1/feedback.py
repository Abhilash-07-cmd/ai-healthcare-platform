from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, RequireRole
from app.models.all_models import User, UserRoleEnum
from app.schemas.feedback import (
    FeedbackCreateRequest, FeedbackResponse,
    FeedbackListResponse, DoctorRatingSummary
)
from app.services.feedback_service import (
    submit_feedback,
    get_my_feedbacks,
    get_doctor_feedbacks,
    get_doctor_rating_summary,
    delete_feedback
)

router = APIRouter(prefix="/feedback", tags=["Patient Feedback & Doctor Ratings"])


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Appointment Feedback",
    description=(
        "Submit a star rating (1–5) and optional written review for a completed appointment. "
        "Automatically updates the doctor's aggregate rating. "
        "One review per appointment per patient."
    )
)
def submit_appointment_feedback(
    payload: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return submit_feedback(db=db, user=current_user, payload=payload)


@router.get(
    "/me",
    response_model=FeedbackListResponse,
    summary="My Submitted Reviews",
    description="Returns all feedback submitted by the currently logged-in patient."
)
def my_feedbacks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_my_feedbacks(db=db, user=current_user)


@router.get(
    "/doctor/{doctor_id}",
    response_model=FeedbackListResponse,
    summary="Doctor Reviews (Public)",
    description="Returns all reviews submitted for a specific doctor. Publicly accessible."
)
def doctor_feedbacks(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    return get_doctor_feedbacks(db=db, doctor_id=doctor_id)


@router.get(
    "/doctor/{doctor_id}/summary",
    response_model=DoctorRatingSummary,
    summary="Doctor Rating Summary",
    description="Returns aggregated rating stats for a doctor: average, total reviews, and star breakdown."
)
def doctor_rating_summary(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    return get_doctor_rating_summary(db=db, doctor_id=doctor_id)


@router.delete(
    "/{feedback_id}",
    summary="Delete Review (Admin Only)",
    description="Permanently deletes a patient review and recalculates the doctor's rating. Admin only."
)
def admin_delete_feedback(
    feedback_id: int,
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    return delete_feedback(db=db, user=current_user, feedback_id=feedback_id)
