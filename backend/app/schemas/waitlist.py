from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time, datetime
from typing import Optional

from app.models.all_models import WaitlistStatusEnum
from app.schemas.profile import DepartmentSimpleResponse


class WaitlistCreate(BaseModel):
    department_id: int
    doctor_id: Optional[int] = None
    preferred_date: date
    preferred_time_slot: Optional[str] = Field("morning", description="morning, afternoon, evening")


class WaitlistResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: Optional[int] = None
    department_id: int
    preferred_date: date
    preferred_time_slot: Optional[str] = None
    position: int
    status: WaitlistStatusEnum
    created_at: datetime
    updated_at: datetime

    department: DepartmentSimpleResponse

    model_config = ConfigDict(from_attributes=True)


class WaitlistAcceptRequest(BaseModel):
    start_time: time
    end_time: time
