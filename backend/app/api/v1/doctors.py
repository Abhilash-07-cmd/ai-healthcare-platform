from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.profile import DoctorProfileResponse, DoctorProfileUpdate
from app.services.profile_service import (
    get_doctor_by_user_id,
    get_doctor_by_id,
    update_doctor_profile,
    search_doctors
)
from app.api.deps import RequireRole
from app.models.all_models import User, UserRoleEnum

router = APIRouter(prefix="/doctors", tags=["Doctor Directory & Profiles"])


@router.get(
    "",
    response_model=List[DoctorProfileResponse],
    summary="Search & List Doctors",
    description="Public endpoint to list and search doctors by department, availability, or keyword query."
)
def list_doctors(
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    is_available: Optional[bool] = Query(None, description="Filter by availability status"),
    search_query: Optional[str] = Query(None, description="Search by doctor name or qualification"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return search_doctors(
        db=db,
        department_id=department_id,
        is_available=is_available,
        search_query=search_query,
        skip=skip,
        limit=limit
    )


@router.get(
    "/me",
    response_model=DoctorProfileResponse,
    summary="Get Doctor's Own Profile",
    description="Retrieves the current authenticated doctor's professional profile."
)
def get_my_doctor_profile(
    current_user: User = Depends(RequireRole([UserRoleEnum.DOCTOR])),
    db: Session = Depends(get_db)
):
    return get_doctor_by_user_id(db=db, user_id=current_user.id)


@router.put(
    "/me",
    response_model=DoctorProfileResponse,
    summary="Update Doctor Profile",
    description="Updates the doctor's qualifications, experience, bio, consultation fee, availability, or department."
)
def update_my_doctor_profile(
    profile_in: DoctorProfileUpdate,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.DOCTOR])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return update_doctor_profile(
        db=db,
        user_id=current_user.id,
        profile_in=profile_in,
        ip_address=ip_address
    )


@router.get(
    "/{id}",
    response_model=DoctorProfileResponse,
    summary="Get Doctor Details by ID",
    description="Public endpoint to view full profile details for a specific doctor by Doctor ID."
)
def get_doctor_details(
    id: int,
    db: Session = Depends(get_db)
):
    return get_doctor_by_id(db=db, doctor_id=id)
