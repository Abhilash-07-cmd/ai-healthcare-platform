from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time, datetime
from typing import Optional, List


# Availability Window Schema
class DoctorAvailabilityItem(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time
    slot_duration_minutes: int = Field(30, ge=10, le=120)


class DoctorAvailabilitySetRequest(BaseModel):
    availability: List[DoctorAvailabilityItem]


class DoctorAvailabilityResponse(DoctorAvailabilityItem):
    id: int
    doctor_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Doctor Leave Schemas
class DoctorLeaveCreate(BaseModel):
    start_date: date
    end_date: date
    reason: Optional[str] = Field(None, max_length=255)


class DoctorLeaveResponse(DoctorLeaveCreate):
    id: int
    doctor_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Appointment Slot Schemas
class SlotGenerationRequest(BaseModel):
    start_date: date
    end_date: date


class AppointmentSlotResponse(BaseModel):
    id: int
    doctor_id: int
    slot_date: date
    start_time: time
    end_time: time
    is_booked: bool

    model_config = ConfigDict(from_attributes=True)
