from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from datetime import datetime

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import engine, SessionLocal
from app.models.base import Base
import app.models.all_models  # Ensure models are imported for metadata creation
from app.services.department_service import seed_default_departments
from app.api.v1.router import api_v1_router
from app.schemas.health import HealthResponse
from app.middleware.audit import AuditLogMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    setup_logging()
    logger.info("Initializing application startup sequence...")
    
    # Auto-create tables if they don't exist
    try:
        logger.info("Creating database tables if not present...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
        
        # Seed default hospital departments
        db = SessionLocal()
        try:
            seed_default_departments(db)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error during startup initialization: {str(e)}")
        
    yield
    
    # Shutdown actions
    logger.info("Application shutdown completed.")


# ── OpenAPI Tags Metadata ─────────────────────────────────────────────────────
tags_metadata = [
    {"name": "Health Check", "description": "Service liveness and health status."},
    {"name": "Authentication & Security", "description": "JWT-based register, login, refresh, and logout flows."},
    {"name": "Patient Profile Management", "description": "Patient profile CRUD and personal health data."},
    {"name": "Doctor Profile Management", "description": "Doctor profile, search, and specialty management."},
    {"name": "Admin Operations", "description": "Platform-wide admin controls: user management, status updates."},
    {"name": "Department Management", "description": "Hospital department creation, listing, and activation control."},
    {"name": "Doctor Availability & Slots", "description": "Weekly working hours, 30-min slot generation, and leave management."},
    {"name": "Appointment Booking & Management", "description": "Full appointment lifecycle: book, confirm, reschedule, cancel, complete."},
    {"name": "Smart Waitlist & Live Queue", "description": "Waitlist registration, slot notification, and real-time clinic queue tracking."},
    {"name": "AI Care Navigator", "description": "Conversational AI assistant for symptom navigation, department routing, and health Q&A."},
    {"name": "Smart Doctor Recommendations", "description": "5-factor AI matching engine for personalized doctor recommendations."},
    {"name": "Notification System", "description": "In-app real-time notifications: welcome alerts, appointment updates, waitlist notifications."},
    {"name": "Medical Document Management", "description": "Secure medical document upload (PDF/image), RAG chunk indexing, and retrieval."},
    {"name": "Admin Analytics & Reporting", "description": "Platform KPIs, revenue stats, department breakdown, and doctor performance dashboards."},
    {"name": "Patient Feedback & Doctor Ratings", "description": "Post-appointment star ratings, written reviews, and live doctor rating aggregation."},
    {"name": "Audit Logs & Security", "description": "Immutable audit trail of all mutating API operations for compliance and security."},
]

app = FastAPI(
    title="AI-Powered Smart Healthcare & Appointment Platform",
    description="""
## 🏥 AI-Powered Smart Healthcare & Appointment Platform

A **production-grade**, full-stack healthcare SaaS built with **FastAPI**, **React 18**, **SQLAlchemy ORM**, and local AI engines — designed as a resume-portfolio showcase for full-stack engineers.

---

### 🚀 Key Features

| Feature | Description |
|---------|-------------|
| **JWT Auth & RBAC** | Secure access/refresh token flow with Patient / Doctor / Admin roles |
| **Smart Doctor Matching** | 5-factor scoring engine (specialty, availability, rating, experience, fee) |
| **AI Care Navigator** | Local intent classification + department routing + safety guardrails |
| **Live Queue Tracking** | Real-time clinic queue with estimated wait times |
| **Smart Waitlist** | Auto-notify eligible waitlisted patients on cancellations |
| **RAG Document Pipeline** | Medical document upload → chunking → vector-store-ready metadata |
| **Analytics Dashboard** | Revenue, KPIs, daily trends, department breakdown |
| **Feedback & Ratings** | Live doctor rating recalculation from patient reviews |
| **Audit Logging** | Immutable API audit trail for compliance |

---

### 🔐 Authentication

All protected endpoints require a **Bearer token** in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Obtain tokens via `POST /api/v1/auth/login`.

---

### 👤 Roles

- **PATIENT** — book appointments, upload documents, leave feedback, chat with AI
- **DOCTOR** — manage availability, view schedule, update appointment status
- **ADMIN** — full platform access including analytics, audit logs, user management
""",
    version="1.0.0",
    contact={
        "name": "Healthcare Platform Team",
        "email": "support@ai-healthcare-platform.dev",
        "url": "https://github.com/your-username/ai-healthcare-platform",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit Logging Middleware (logs all mutating API calls to audit_logs table)
app.add_middleware(AuditLogMiddleware)

# Request timing & logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"HTTP {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.2f}ms"
    )
    return response


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception at {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please contact system support.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Root Health Endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health Check"])
def root_health():
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        timestamp=datetime.utcnow()
    )


# Include API V1 Router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
