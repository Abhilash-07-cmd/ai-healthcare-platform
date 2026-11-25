from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from app.schemas.user import UserResponse
from app.models.all_models import UserRoleEnum


# Patient Profile Schemas
class PatientProfileBase(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    blood_group: Optional[str] = Field(None, max_length=10)
    emergency_contact: Optional[str] = Field(None, max_length=100)
    medical_history_summary: Optional[str] = None


class PatientProfileUpdate(PatientProfileBase):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)


class PatientProfileResponse(PatientProfileBase):
    id: int
    user_id: int
    user: UserResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Department Metadata Schema for Doctor
class DepartmentSimpleResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    icon: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Doctor Profile Schemas
class DoctorProfileBase(BaseModel):
    qualification: str = Field(..., max_length=255)
    experience_years: int = Field(0, ge=0)
    bio: Optional[str] = None
    consultation_fee: float = Field(500.0, ge=0.0)
    is_available: bool = True


class DoctorProfileUpdate(BaseModel):
    qualification: Optional[str] = Field(None, max_length=255)
    experience_years: Optional[int] = Field(None, ge=0)
    bio: Optional[str] = None
    consultation_fee: Optional[float] = Field(None, ge=0.0)
    is_available: Optional[bool] = None
    department_id: Optional[int] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)


class DoctorProfileResponse(DoctorProfileBase):
    id: int
    user_id: int
    department_id: int
    rating: float
    created_at: datetime
    user: UserResponse
    department: DepartmentSimpleResponse

    model_config = ConfigDict(from_attributes=True)


# Admin User Schemas
class AdminUserStatusUpdate(BaseModel):
    is_active: bool


class AdminUserRoleUpdate(BaseModel):
    role: UserRoleEnum
