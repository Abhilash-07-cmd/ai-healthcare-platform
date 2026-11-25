from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    app_name: str
    environment: str
    timestamp: datetime

class DatabaseHealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    database: str
    dialect: str
    ping_response: bool
    timestamp: datetime
    error: Optional[str] = None
