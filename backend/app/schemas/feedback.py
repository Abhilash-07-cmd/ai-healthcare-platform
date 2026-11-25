from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List


class FeedbackCreateRequest(BaseModel):
    appointment_id: int = Field(..., description="ID of the completed appointment being reviewed")
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 (poor) to 5 (excellent)")
    comments: Optional[str] = Field(None, max_length=1000, description="Optional written review")

    @field_validator("rating")
    @classmethod
    def rating_must_be_valid(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class FeedbackResponse(BaseModel):
    id: int
    appointment_id: int
    rating: int
    comments: Optional[str] = None
    created_at: datetime

    # Enriched fields (computed, not DB columns)
    doctor_name: Optional[str] = None
    patient_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FeedbackListResponse(BaseModel):
    total: int
    average_rating: float
    feedbacks: List[FeedbackResponse]


class DoctorRatingSummary(BaseModel):
    doctor_id: int
    doctor_name: str
    department: str
    total_reviews: int
    average_rating: float
    rating_breakdown: dict  # {1: count, 2: count, ...5: count}
