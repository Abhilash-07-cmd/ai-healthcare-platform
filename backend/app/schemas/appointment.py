from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time, datetime
from typing import Optional, List

from app.models.all_models import AppointmentStatusEnum, AppointmentTypeEnum
from app.schemas.user import UserResponse
from app.schemas.profile import PatientProfileResponse, DoctorProfileResponse, DepartmentSimpleResponse


class AppointmentCreate(BaseModel):
    doctor_id: int
    department_id: int
    appointment_date: date
    start_time: time
    end_time: time
    appointment_type: AppointmentTypeEnum = AppointmentTypeEnum.IN_PERSON
    reason_for_visit: Optional[str] = Field(None, max_length=500)


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatusEnum] = None
    notes: Optional[str] = None
    queue_number: Optional[int] = None


class AppointmentReschedule(BaseModel):
    new_date: date
    new_start_time: time
    new_end_time: time
    reason: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    department_id: int
    appointment_date: date
    start_time: time
    end_time: time
    appointment_type: AppointmentTypeEnum
    status: AppointmentStatusEnum
    reason_for_visit: Optional[str] = None
    notes: Optional[str] = None
    queue_number: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    patient: PatientProfileResponse
    doctor: DoctorProfileResponse
    department: DepartmentSimpleResponse

    model_config = ConfigDict(from_attributes=True)
