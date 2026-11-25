from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import List, Optional, Tuple

from app.models.all_models import User, Patient, Doctor, Department, UserRoleEnum
from app.schemas.profile import PatientProfileUpdate, DoctorProfileUpdate
from app.services.audit_service import create_audit_log


# Patient Profile Services
def get_patient_by_user_id(db: Session, user_id: int) -> Patient:
    patient = (
        db.query(Patient)
        .options(joinedload(Patient.user))
        .filter(Patient.user_id == user_id)
        .first()
    )
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found."
        )
    return patient


def update_patient_profile(db: Session, user_id: int, profile_in: PatientProfileUpdate, ip_address: Optional[str] = None) -> Patient:
    patient = get_patient_by_user_id(db, user_id)
    user = patient.user

    # Update User attributes if provided
    if profile_in.full_name is not None:
        user.full_name = profile_in.full_name
    if profile_in.phone is not None:
        user.phone = profile_in.phone

    # Update Patient profile attributes if provided
    if profile_in.date_of_birth is not None:
        patient.date_of_birth = profile_in.date_of_birth
    if profile_in.gender is not None:
        patient.gender = profile_in.gender
    if profile_in.blood_group is not None:
        patient.blood_group = profile_in.blood_group
    if profile_in.emergency_contact is not None:
        patient.emergency_contact = profile_in.emergency_contact
    if profile_in.medical_history_summary is not None:
        patient.medical_history_summary = profile_in.medical_history_summary

    db.commit()
    db.refresh(patient)
    db.refresh(user)

    create_audit_log(
        db=db,
        action="UPDATE_PATIENT_PROFILE",
        resource="patients",
        user_id=user_id,
        resource_id=str(patient.id),
        details={"updated_by": user_id},
        ip_address=ip_address
    )

    return patient


# Doctor Profile Services
def get_doctor_by_user_id(db: Session, user_id: int) -> Doctor:
    doctor = (
        db.query(Doctor)
        .options(joinedload(Doctor.user), joinedload(Doctor.department))
        .filter(Doctor.user_id == user_id)
        .first()
    )
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found."
        )
    return doctor


def get_doctor_by_id(db: Session, doctor_id: int) -> Doctor:
    doctor = (
        db.query(Doctor)
        .options(joinedload(Doctor.user), joinedload(Doctor.department))
        .filter(Doctor.id == doctor_id)
        .first()
    )
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {doctor_id} not found."
        )
    return doctor


def update_doctor_profile(db: Session, user_id: int, profile_in: DoctorProfileUpdate, ip_address: Optional[str] = None) -> Doctor:
    doctor = get_doctor_by_user_id(db, user_id)
    user = doctor.user

    if profile_in.full_name is not None:
        user.full_name = profile_in.full_name
    if profile_in.phone is not None:
        user.phone = profile_in.phone

    if profile_in.qualification is not None:
        doctor.qualification = profile_in.qualification
    if profile_in.experience_years is not None:
        doctor.experience_years = profile_in.experience_years
    if profile_in.bio is not None:
        doctor.bio = profile_in.bio
    if profile_in.consultation_fee is not None:
        doctor.consultation_fee = profile_in.consultation_fee
    if profile_in.is_available is not None:
        doctor.is_available = profile_in.is_available
    if profile_in.department_id is not None:
        dept = db.query(Department).filter(Department.id == profile_in.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid department_id specified."
            )
        doctor.department_id = profile_in.department_id

    db.commit()
    db.refresh(doctor)
    db.refresh(user)

    create_audit_log(
        db=db,
        action="UPDATE_DOCTOR_PROFILE",
        resource="doctors",
        user_id=user_id,
        resource_id=str(doctor.id),
        details={"updated_by": user_id},
        ip_address=ip_address
    )

    return doctor


def search_doctors(
    db: Session,
    department_id: Optional[int] = None,
    is_available: Optional[bool] = None,
    search_query: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Doctor]:
    query = db.query(Doctor).options(joinedload(Doctor.user), joinedload(Doctor.department))

    if department_id is not None:
        query = query.filter(Doctor.department_id == department_id)

    if is_available is not None:
        query = query.filter(Doctor.is_available == is_available)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.join(User).filter(
            (User.full_name.ilike(search_pattern)) |
            (Doctor.qualification.ilike(search_pattern)) |
            (Doctor.bio.ilike(search_pattern))
        )

    return query.offset(skip).limit(limit).all()


# Admin Services
def admin_list_users(
    db: Session,
    role: Optional[UserRoleEnum] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50
) -> List[User]:
    query = db.query(User)
    if role is not None:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.order_by(User.id.desc()).offset(skip).limit(limit).all()


def admin_toggle_user_active(db: Session, target_user_id: int, is_active: bool, admin_user_id: int, ip_address: Optional[str] = None) -> User:
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    user.is_active = is_active
    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        action="ADMIN_TOGGLE_USER_STATUS",
        resource="users",
        user_id=admin_user_id,
        resource_id=str(user.id),
        details={"target_user": user.email, "new_status": is_active},
        ip_address=ip_address
    )

    return user


def admin_update_user_role(db: Session, target_user_id: int, new_role: UserRoleEnum, admin_user_id: int, ip_address: Optional[str] = None) -> User:
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    old_role = user.role
    user.role = new_role
    
    # Ensure profile records exist for converted role
    if new_role == UserRoleEnum.PATIENT and not user.patient_profile:
        patient_profile = Patient(user_id=user.id)
        db.add(patient_profile)
    elif new_role == UserRoleEnum.DOCTOR and not user.doctor_profile:
        default_dept = db.query(Department).first()
        if not default_dept:
            default_dept = Department(name="General Medicine", code="GEN_MED", description="General Medicine")
            db.add(default_dept)
            db.commit()
            db.refresh(default_dept)
        doctor_profile = Doctor(user_id=user.id, department_id=default_dept.id, qualification="MBBS")
        db.add(doctor_profile)

    db.commit()
    db.refresh(user)

    create_audit_log(
        db=db,
        action="ADMIN_UPDATE_USER_ROLE",
        resource="users",
        user_id=admin_user_id,
        resource_id=str(user.id),
        details={"target_user": user.email, "old_role": old_role.value, "new_role": new_role.value},
        ip_address=ip_address
    )

    return user
