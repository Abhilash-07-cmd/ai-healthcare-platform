from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app.core.config import settings
from app.core.database import get_db
from app.schemas.health import HealthResponse, DatabaseHealthResponse

router = APIRouter(tags=["Health Check"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Get Application System Health Status",
    description="Returns the overall operational health status, application name, environment, and current timestamp."
)
def get_health():
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        timestamp=datetime.utcnow()
    )


@router.get(
    "/health/db",
    response_model=DatabaseHealthResponse,
    summary="Get Database Connectivity Status",
    description="Executes a live query (`SELECT 1`) on the configured database engine (MySQL/SQLite) and returns connection status."
)
def get_db_health(db: Session = Depends(get_db)):
    try:
        # Execute test ping query
        db.execute(text("SELECT 1"))
        dialect = db.bind.dialect.name if db.bind else "unknown"
        
        return DatabaseHealthResponse(
            status="healthy",
            database="connected",
            dialect=dialect,
            ping_response=True,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        return DatabaseHealthResponse(
            status="unhealthy",
            database="disconnected",
            dialect="unknown",
            ping_response=False,
            timestamp=datetime.utcnow(),
            error=str(e)
        )
