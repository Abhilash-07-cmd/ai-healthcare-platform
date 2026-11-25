from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional, List


class DoctorMatchRequest(BaseModel):
    department_id: Optional[int] = None
    specialty_keyword: Optional[str] = None
    preferred_date: Optional[date] = None
    max_fee: Optional[float] = None
    min_rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)
    appointment_type: Optional[str] = None
    limit: Optional[int] = Field(default=10, ge=1, le=50)


class DoctorMatchScore(BaseModel):
    doctor_id: int
    name: str
    department: str
    department_id: int
    qualification: str
    experience_years: int
    rating: float
    consultation_fee: float
    is_available: bool
    match_score: int = Field(..., ge=0, le=100)
    match_reasons: List[str]

    model_config = ConfigDict(from_attributes=True)


class DoctorMatchResponse(BaseModel):
    query_summary: str
    total_matched: int
    doctors: List[DoctorMatchScore]
