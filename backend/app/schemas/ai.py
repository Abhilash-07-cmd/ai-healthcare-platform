from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


class ChatConversationCreate(BaseModel):
    title: Optional[str] = "Healthcare Consultation"
    language: Optional[str] = "English"


class ChatMessageResponse(BaseModel):
    id: int
    sender: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatConversationResponse(BaseModel):
    id: int
    patient_id: int
    title: str
    language: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[ChatMessageResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class ChatConversationListItem(BaseModel):
    id: int
    title: str
    language: str
    created_at: datetime
    message_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str = Field(..., min_length=1, max_length=2000)
    language: Optional[str] = "English"


class RecommendedDoctorInfo(BaseModel):
    id: int
    name: str
    department: str
    qualification: str
    consultation_fee: float
    rating: float
    match_reason: str

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str
    recommended_department: Optional[str] = None
    recommended_doctors: Optional[List[RecommendedDoctorInfo]] = []
    disclaimer_triggered: bool = False
    disclaimer_message: Optional[str] = None
