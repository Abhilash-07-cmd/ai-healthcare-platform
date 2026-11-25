from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.schemas.recommendation import DoctorMatchRequest, DoctorMatchResponse
from app.services.recommendation_service import get_doctor_recommendations, get_quick_recommendations
from app.api.deps import get_current_user
from app.models.all_models import User

router = APIRouter(prefix="/recommendations", tags=["Doctor Recommendation Engine"])


@router.post(
    "/doctors",
    response_model=DoctorMatchResponse,
    summary="Get Ranked Doctor Recommendations with Match Scores",
    description=(
        "Returns a ranked list of doctors with transparent 0-100 match scores and "
        "human-readable match reasons based on specialty, availability, rating, experience, and fee filters."
    )
)
def recommend_doctors(
    request: DoctorMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_doctor_recommendations(db=db, request=request)


@router.get(
    "/doctors/quick",
    response_model=DoctorMatchResponse,
    summary="Quick Top-3 Department Recommendations",
    description="Returns the top 3 highest-scored available doctors in a specified department."
)
def quick_recommendations(
    department_id: int = Query(..., description="Department ID to get quick recommendations for"),
    limit: Optional[int] = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_quick_recommendations(db=db, department_id=department_id, limit=limit)
