from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Dermatology"})
    code: str = Field(..., min_length=2, max_length=20, json_schema_extra={"example": "DERM"})
    description: Optional[str] = None
    icon: Optional[str] = Field("stethoscope", max_length=100)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    id: int
    is_active: bool
    created_at: datetime
    doctor_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
