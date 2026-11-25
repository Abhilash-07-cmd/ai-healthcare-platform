from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest
from app.services.auth_service import register_user, authenticate_user, refresh_user_token
from app.services.audit_service import create_audit_log
from app.api.deps import get_current_user
from app.models.all_models import User

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new User (Patient, Doctor, or Admin)",
    description="Registers a new user, hashes password, initializes patient or doctor profile based on role, and returns JWT tokens."
)
def register(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    user, access_token, refresh_token = register_user(db=db, user_in=user_in, ip_address=ip_address)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="JSON Login",
    description="Authenticates user with JSON payload (email & password) and returns JWT access and refresh tokens."
)
def login(
    login_in: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    user, access_token, refresh_token = authenticate_user(
        db=db,
        email=login_in.email,
        password=login_in.password,
        ip_address=ip_address
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/login-form",
    response_model=TokenResponse,
    summary="OAuth2 Form Login (Swagger UI Compatible)",
    description="Authenticates user via standard OAuth2 form fields (username=email, password) for FastAPI Swagger UI login integration."
)
def login_form(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    user, access_token, refresh_token = authenticate_user(
        db=db,
        email=form_data.username,
        password=form_data.password,
        ip_address=ip_address
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Access Token",
    description="Validates refresh token and returns a fresh pair of access and refresh JWT tokens."
)
def refresh(
    refresh_in: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    user, access_token, refresh_token = refresh_user_token(
        db=db,
        refresh_token=refresh_in.refresh_token
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current Authenticated User Profile",
    description="Returns the profile metadata for the currently authenticated user identified by the Bearer access token."
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/logout",
    summary="User Logout",
    description="Records user logout action in audit log."
)
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    create_audit_log(
        db=db,
        action="USER_LOGOUT",
        resource="users",
        user_id=current_user.id,
        resource_id=str(current_user.id),
        details={"email": current_user.email},
        ip_address=ip_address
    )
    return {"message": "Successfully logged out."}
