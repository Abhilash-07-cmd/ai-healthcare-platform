from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.patients import router as patients_router
from app.api.v1.doctors import router as doctors_router
from app.api.v1.admin import router as admin_router
from app.api.v1.departments import router as departments_router
from app.api.v1.availability import router as availability_router
from app.api.v1.appointments import router as appointments_router
from app.api.v1.waitlist import router as waitlist_router
from app.api.v1.queue import router as queue_router
from app.api.v1.ai import router as ai_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.documents import router as documents_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.audit import router as audit_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(patients_router)
api_v1_router.include_router(doctors_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(departments_router)
api_v1_router.include_router(availability_router)
api_v1_router.include_router(appointments_router)
api_v1_router.include_router(waitlist_router)
api_v1_router.include_router(queue_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(feedback_router)
api_v1_router.include_router(audit_router)
