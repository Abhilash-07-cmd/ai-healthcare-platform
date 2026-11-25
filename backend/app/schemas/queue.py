from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time, datetime
from typing import Optional, List


class LiveQueueStatusResponse(BaseModel):
    doctor_id: int
    doctor_name: str
    department_name: str
    date: date
    patients_ahead: int
    current_serving_queue_number: int
    patient_queue_number: Optional[int] = None
    estimated_waiting_time_minutes: int
    disclaimer: str = "Estimated waiting time is approximate and based on average 15-minute consultation durations."
    currently_serving_status: str

    model_config = ConfigDict(from_attributes=True)
