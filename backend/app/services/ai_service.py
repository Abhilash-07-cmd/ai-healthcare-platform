from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import Optional, List
import logging

from app.models.all_models import (
    Conversation, Message, Patient, Doctor, Department, User
)
from app.schemas.ai import (
    ChatConversationCreate, ChatRequest, ChatResponse,
    RecommendedDoctorInfo
)
from app.core.prompts import SYSTEM_CARE_NAVIGATOR_PROMPT, MEDICAL_SAFETY_KEYWORDS
from app.services.profile_service import get_patient_by_user_id

logger = logging.getLogger("healthcare_platform.ai_service")

MEDICAL_DISCLAIMER = (
    "⚠️ **Medical Safety Notice**: I am an administrative care navigation assistant only. "
    "I cannot diagnose medical conditions, recommend medications, or prescribe treatments. "
    "**Please consult a licensed physician immediately** or call emergency services (112 / 911) "
    "if you are experiencing a medical emergency."
)

# Department keyword mapping for intent classification
DEPARTMENT_INTENT_MAP = {
    "skin": "Dermatology",
    "dermatolog": "Dermatology",
    "acne": "Dermatology",
    "rash": "Dermatology",
    "heart": "Cardiology",
    "cardio": "Cardiology",
    "chest": "Cardiology",
    "bone": "Orthopedics",
    "joint": "Orthopedics",
    "fracture": "Orthopedics",
    "ortho": "Orthopedics",
    "brain": "Neurology",
    "neuro": "Neurology",
    "headache": "Neurology",
    "migraine": "Neurology",
    "eye": "Ophthalmology",
    "vision": "Ophthalmology",
    "teeth": "Dentistry",
    "dental": "Dentistry",
    "tooth": "Dentistry",
    "child": "Pediatrics",
    "kid": "Pediatrics",
    "pediatr": "Pediatrics",
    "baby": "Pediatrics",
    "mental": "Psychiatry",
    "anxiety": "Psychiatry",
    "depression": "Psychiatry",
    "psych": "Psychiatry",
    "stomach": "Gastroenterology",
    "digestive": "Gastroenterology",
    "gastro": "Gastroenterology",
    "cancer": "Oncology",
    "oncolog": "Oncology",
    "kidney": "Nephrology",
    "urology": "Urology",
    "lung": "Pulmonology",
    "asthma": "Pulmonology",
    "thyroid": "Endocrinology",
    "diabetes": "Endocrinology",
    "general": "General Medicine",
    "fever": "General Medicine",
    "cold": "General Medicine",
    "flu": "General Medicine",
}


def _detect_safety_flag(message: str) -> bool:
    """Returns True if message contains safety-critical diagnostic query keywords."""
    lower = message.lower()
    return any(kw in lower for kw in MEDICAL_SAFETY_KEYWORDS)


def _classify_department(message: str) -> Optional[str]:
    """Returns the best-matching department name from message keywords."""
    lower = message.lower()
    for keyword, dept_name in DEPARTMENT_INTENT_MAP.items():
        if keyword in lower:
            return dept_name
    return None


def _get_recommended_doctors(
    db: Session,
    department_name: str,
    limit: int = 3
) -> List[RecommendedDoctorInfo]:
    dept = db.query(Department).filter(
        Department.name.ilike(f"%{department_name}%"),
        Department.is_active == True
    ).first()

    if not dept:
        return []

    doctors = (
        db.query(Doctor)
        .options(joinedload(Doctor.user), joinedload(Doctor.department))
        .filter(Doctor.department_id == dept.id, Doctor.is_available == True)
        .order_by(Doctor.rating.desc())
        .limit(limit)
        .all()
    )

    results = []
    for doc in doctors:
        results.append(RecommendedDoctorInfo(
            id=doc.id,
            name=doc.user.full_name,
            department=doc.department.name,
            qualification=doc.qualification,
            consultation_fee=float(doc.consultation_fee or 0),
            rating=float(doc.rating or 0.0),
            match_reason=f"Specialist in {dept.name} with {doc.experience_years or 0}+ years of experience"
        ))
    return results


def _build_ai_reply(
    message: str,
    department_name: Optional[str],
    doctors: List[RecommendedDoctorInfo],
    safety_triggered: bool,
    language: str = "English"
) -> str:
    lower = message.lower()

    if safety_triggered:
        return MEDICAL_DISCLAIMER

    if "appointment" in lower or "book" in lower or "schedule" in lower:
        if department_name and doctors:
            doc_list = "\n".join([f"- **Dr. {d.name}** ({d.department}) — ₹{d.consultation_fee} fee | ⭐ {d.rating}" for d in doctors])
            return (
                f"I can help you book an appointment! Based on your request, I recommend the **{department_name}** department.\n\n"
                f"**Available Specialists:**\n{doc_list}\n\n"
                f"Click **Book Appointment** on the doctor's profile, or navigate to **Find Doctors** in the sidebar to explore more options."
            )
        return (
            "I can help you book an appointment! Please head to **Find Doctors** in the sidebar and select your preferred department and specialist."
        )

    if "waitlist" in lower or "wait list" in lower:
        return (
            "To join the **Smart Waitlist**, navigate to the **Waitlist** section in your sidebar. "
            "You'll receive an automatic notification if a slot opens up for your preferred date and department."
        )

    if "queue" in lower or "waiting time" in lower or "how long" in lower:
        return (
            "You can check the **Live Clinic Queue** status on your dashboard. "
            "It shows estimated waiting time and how many patients are ahead of you."
        )

    if department_name and doctors:
        doc_list = "\n".join([f"- **Dr. {d.name}** ({d.qualification}) — ₹{d.consultation_fee} | ⭐ {d.rating}" for d in doctors])
        return (
            f"I found the **{department_name}** department matches your request.\n\n"
            f"**Top Recommended Specialists:**\n{doc_list}\n\n"
            f"Would you like me to help you book a slot with one of these doctors?"
        )

    return (
        "I'm here to help you navigate our healthcare services!\n\n"
        "I can assist you with:\n"
        "- 🏥 **Finding the right department or specialist**\n"
        "- 📅 **Booking, rescheduling, or cancelling appointments**\n"
        "- 🕐 **Checking live queue status and waiting time**\n"
        "- 📋 **Joining the smart waitlist when slots are full**\n\n"
        "What would you like help with today?"
    )


def create_conversation(
    db: Session,
    patient_user_id: int,
    conv_in: ChatConversationCreate
) -> Conversation:
    patient = get_patient_by_user_id(db, patient_user_id)

    conv = Conversation(
        patient_id=patient.id,
        title=conv_in.title or "Healthcare Consultation",
        language=conv_in.language or "English"
    )
    db.add(conv)

    # Add system prompt as first message
    system_msg = Message(
        conversation_id=None,  # will be set after flush
        sender="system",
        content=SYSTEM_CARE_NAVIGATOR_PROMPT.strip()
    )
    db.flush()
    system_msg.conversation_id = conv.id
    db.add(system_msg)
    db.commit()
    db.refresh(conv)
    return conv


def get_patient_conversations(db: Session, patient_user_id: int) -> List[Conversation]:
    patient = get_patient_by_user_id(db, patient_user_id)
    return (
        db.query(Conversation)
        .filter(Conversation.patient_id == patient.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


def get_conversation_messages(
    db: Session,
    conversation_id: int,
    patient_user_id: int
) -> Conversation:
    patient = get_patient_by_user_id(db, patient_user_id)
    conv = (
        db.query(Conversation)
        .options(joinedload(Conversation.messages))
        .filter(
            Conversation.id == conversation_id,
            Conversation.patient_id == patient.id
        )
        .first()
    )
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found."
        )
    return conv


def process_chat_message(
    db: Session,
    patient_user_id: int,
    chat_in: ChatRequest
) -> ChatResponse:
    patient = get_patient_by_user_id(db, patient_user_id)

    # Resolve or create conversation session
    if chat_in.conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == chat_in.conversation_id,
            Conversation.patient_id == patient.id
        ).first()
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation session not found."
            )
    else:
        conv_in = ChatConversationCreate(
            title=chat_in.message[:80],
            language=chat_in.language or "English"
        )
        conv = create_conversation(db, patient_user_id, conv_in)

    # Persist user message
    user_msg = Message(
        conversation_id=conv.id,
        sender="user",
        content=chat_in.message
    )
    db.add(user_msg)
    db.flush()

    # Core AI Processing Pipeline
    safety_triggered = _detect_safety_flag(chat_in.message)
    department_name = None
    doctors = []

    if not safety_triggered:
        department_name = _classify_department(chat_in.message)
        if department_name:
            doctors = _get_recommended_doctors(db, department_name)

    reply = _build_ai_reply(
        message=chat_in.message,
        department_name=department_name,
        doctors=doctors,
        safety_triggered=safety_triggered,
        language=chat_in.language or "English"
    )

    # Persist assistant reply message
    assistant_msg = Message(
        conversation_id=conv.id,
        sender="assistant",
        content=reply
    )
    db.add(assistant_msg)

    # Update conversation timestamp
    from datetime import datetime
    conv.updated_at = datetime.utcnow()
    db.commit()

    return ChatResponse(
        conversation_id=conv.id,
        reply=reply,
        recommended_department=department_name,
        recommended_doctors=doctors,
        disclaimer_triggered=safety_triggered,
        disclaimer_message=MEDICAL_DISCLAIMER if safety_triggered else None
    )
