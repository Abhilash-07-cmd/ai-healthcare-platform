from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.profile import PatientProfileResponse, PatientProfileUpdate
from app.services.profile_service import get_patient_by_user_id, update_patient_profile
from app.api.deps import get_current_user, RequireRole
from app.models.all_models import User, UserRoleEnum

router = APIRouter(prefix="/patients", tags=["Patient Profiles"])


@router.get(
    "/me",
    response_model=PatientProfileResponse,
    summary="Get Patient Profile",
    description="Retrieves the current authenticated patient's profile details including DOB, gender, blood group, and emergency contact."
)
def get_my_patient_profile(
    current_user: User = Depends(RequireRole([UserRoleEnum.PATIENT])),
    db: Session = Depends(get_db)
):
    return get_patient_by_user_id(db=db, user_id=current_user.id)


@router.put(
    "/me",
    response_model=PatientProfileResponse,
    summary="Update Patient Profile",
    description="Updates the current patient's personal metadata (DOB, gender, blood group, emergency contact, medical history)."
)
def update_my_patient_profile(
    profile_in: PatientProfileUpdate,
    request: Request,
    current_user: User = Depends(RequireRole([UserRoleEnum.PATIENT])),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    return update_patient_profile(
        db=db,
        user_id=current_user.id,
        profile_in=profile_in,
        ip_address=ip_address
    )
