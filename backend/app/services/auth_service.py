from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Tuple, Optional

from app.models.all_models import User, Patient, Doctor, Department, UserRoleEnum, Notification
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.services.audit_service import create_audit_log


def register_user(db: Session, user_in: UserCreate, ip_address: Optional[str] = None) -> Tuple[User, str, str]:
    """
    Registers a new user, hashes password, initializes role profile (Patient or Doctor),
    records audit log, and returns (user, access_token, refresh_token).
    """
    # Check duplicate email
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Hash password & create user
    hashed_pwd = hash_password(user_in.password)
    db_user = User(
        email=user_in.email,
        password_hash=hashed_pwd,
        full_name=user_in.full_name,
        role=user_in.role,
        phone=user_in.phone,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Initialize role-specific profile
    if user_in.role == UserRoleEnum.PATIENT:
        patient_profile = Patient(user_id=db_user.id)
        db.add(patient_profile)
    elif user_in.role == UserRoleEnum.DOCTOR:
        # Check or create default General Medicine department for initial doctor setup
        default_dept = db.query(Department).filter(Department.code == "GEN_MED").first()
        if not default_dept:
            default_dept = Department(
                name="General Medicine",
                code="GEN_MED",
                description="General health and primary healthcare consultations",
                icon="stethoscope"
            )
            db.add(default_dept)
            db.commit()
            db.refresh(default_dept)
            
        doctor_profile = Doctor(
            user_id=db_user.id,
            department_id=default_dept.id,
            qualification="MBBS",
            experience_years=5,
            consultation_fee=500.0
        )
        db.add(doctor_profile)

    db.commit()
    db.refresh(db_user)

    # Welcome notification
    welcome_notif = Notification(
        user_id=db_user.id,
        title="Welcome to SmartHealth! 🏥",
        message=(
            f"Hi {db_user.full_name}, welcome to the AI-Powered Smart Healthcare Platform! "
            "You can now book appointments, consult our AI Care Navigator, and manage your health journey."
        ),
        notification_type="WELCOME",
        is_read=False
    )
    db.add(welcome_notif)
    db.commit()

    # Audit log
    create_audit_log(
        db=db,
        action="USER_REGISTER",
        resource="users",
        user_id=db_user.id,
        resource_id=str(db_user.id),
        details={"email": db_user.email, "role": db_user.role.value},
        ip_address=ip_address
    )

    # Tokens
    access_token = create_access_token(subject=db_user.id, role=db_user.role.value)
    refresh_token = create_refresh_token(subject=db_user.id, role=db_user.role.value)

    return db_user, access_token, refresh_token


def authenticate_user(db: Session, email: str, password: str, ip_address: Optional[str] = None) -> Tuple[User, str, str]:
    """
    Authenticates user credentials, records audit log, and returns (user, access_token, refresh_token).
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Please contact administration."
        )

    # Audit Log
    create_audit_log(
        db=db,
        action="USER_LOGIN",
        resource="users",
        user_id=user.id,
        resource_id=str(user.id),
        details={"email": user.email, "role": user.role.value},
        ip_address=ip_address
    )

    access_token = create_access_token(subject=user.id, role=user.role.value)
    refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

    return user, access_token, refresh_token


def refresh_user_token(db: Session, refresh_token: str) -> Tuple[User, str, str]:
    """
    Validates a refresh token and generates a new pair of access and refresh tokens.
    """
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP01_UNAUTHORIZED if not user else status.HTTP_403_FORBIDDEN,
            detail="User not found or inactive."
        )

    new_access_token = create_access_token(subject=user.id, role=user.role.value)
    new_refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

    return user, new_access_token, new_refresh_token
