from sqlalchemy.orm import Session, joinedload
from datetime import date
from typing import List, Optional
import logging

from app.models.all_models import Doctor, Department, AppointmentSlot
from app.schemas.recommendation import DoctorMatchRequest, DoctorMatchScore, DoctorMatchResponse

logger = logging.getLogger("healthcare_platform.recommendation_service")

# Scoring weights
WEIGHT_SPECIALTY_MATCH = 40
WEIGHT_AVAILABILITY = 20
WEIGHT_RATING = 20
WEIGHT_EXPERIENCE = 10
WEIGHT_FEE_RANGE = 10


def _score_doctor(
    doctor: Doctor,
    request: DoctorMatchRequest,
    has_availability: bool
) -> Optional[DoctorMatchScore]:
    """Compute multi-factor match score for a single doctor."""
    score = 0
    reasons = []

    dept_name = doctor.department.name if doctor.department else ""
    qualification = doctor.qualification or ""
    experience = doctor.experience_years or 0
    rating = float(doctor.rating or 0.0)
    fee = float(doctor.consultation_fee or 0.0)

    # --- 1. Specialty Match (+40 pts) ---
    specialty_matched = False
    if request.department_id and doctor.department_id == request.department_id:
        score += WEIGHT_SPECIALTY_MATCH
        reasons.append(f"Specialty match: {dept_name}")
        specialty_matched = True
    elif request.specialty_keyword:
        kw = request.specialty_keyword.lower()
        if kw in dept_name.lower() or kw in qualification.lower():
            score += WEIGHT_SPECIALTY_MATCH
            reasons.append(f"Keyword match: '{request.specialty_keyword}' in {dept_name}")
            specialty_matched = True

    # If no specialty filter provided at all, give partial credit
    if not request.department_id and not request.specialty_keyword:
        score += WEIGHT_SPECIALTY_MATCH
        reasons.append(f"Department: {dept_name}")

    # --- 2. Availability Check (+20 pts) ---
    if has_availability:
        score += WEIGHT_AVAILABILITY
        if request.preferred_date:
            reasons.append(f"Available on {request.preferred_date}")
        else:
            reasons.append("Has open appointment slots")
    else:
        if request.preferred_date:
            reasons.append(f"No open slots on {request.preferred_date}")

    # --- 3. Rating Score (+20 pts) ---
    if rating > 0:
        rating_pts = round((rating / 5.0) * WEIGHT_RATING)
        score += rating_pts
        if rating >= 4.5:
            reasons.append(f"Highly rated: {rating} ⭐")
        elif rating >= 3.5:
            reasons.append(f"Well rated: {rating} ⭐")
        else:
            reasons.append(f"Rating: {rating} ⭐")

    # --- 4. Experience Score (+10 pts) ---
    exp_pts = min(experience, WEIGHT_EXPERIENCE)
    score += exp_pts
    if experience > 0:
        reasons.append(f"{experience}+ years of clinical experience")

    # --- 5. Fee Range Filter (+10 pts) ---
    if request.max_fee is not None:
        if fee > request.max_fee:
            return None  # Exclude: exceeds budget
        fee_pts = round((1 - (fee / max(request.max_fee, 1))) * WEIGHT_FEE_RANGE)
        score += max(0, fee_pts)
        reasons.append(f"Within budget: ₹{fee} (max ₹{request.max_fee})")
    else:
        score += WEIGHT_FEE_RANGE
        reasons.append(f"Consultation fee: ₹{fee}")

    # --- Min Rating Filter ---
    if request.min_rating and rating < request.min_rating:
        return None  # Exclude: below minimum rating

    return DoctorMatchScore(
        doctor_id=doctor.id,
        name=doctor.user.full_name,
        department=dept_name,
        department_id=doctor.department_id,
        qualification=qualification,
        experience_years=experience,
        rating=rating,
        consultation_fee=fee,
        is_available=has_availability,
        match_score=min(100, score),
        match_reasons=reasons
    )


def _check_doctor_availability(db: Session, doctor_id: int, target_date: Optional[date]) -> bool:
    """Returns True if doctor has at least one open slot on target_date (or any date if None)."""
    query = db.query(AppointmentSlot).filter(
        AppointmentSlot.doctor_id == doctor_id,
        AppointmentSlot.is_booked == False
    )
    if target_date:
        query = query.filter(AppointmentSlot.slot_date == target_date)

    return query.first() is not None


def get_doctor_recommendations(
    db: Session,
    request: DoctorMatchRequest
) -> DoctorMatchResponse:
    """Main recommendation engine: score, filter, and rank all eligible doctors."""

    # Load all available doctors with relationships
    doctors_query = (
        db.query(Doctor)
        .options(
            joinedload(Doctor.user),
            joinedload(Doctor.department)
        )
        .filter(Doctor.is_available == True)
    )

    # Pre-filter by department if given
    if request.department_id:
        doctors_query = doctors_query.filter(Doctor.department_id == request.department_id)

    all_doctors = doctors_query.all()

    scored = []
    for doc in all_doctors:
        has_avail = _check_doctor_availability(db, doc.id, request.preferred_date)
        result = _score_doctor(doc, request, has_avail)
        if result is not None:
            scored.append(result)

    # Sort by match_score descending, then by rating
    scored.sort(key=lambda d: (d.match_score, d.rating), reverse=True)

    # Apply limit
    limited = scored[: request.limit or 10]

    # Build query summary string
    parts = []
    if request.specialty_keyword:
        parts.append(f"keyword '{request.specialty_keyword}'")
    if request.department_id:
        dept = db.query(Department).filter(Department.id == request.department_id).first()
        parts.append(f"department '{dept.name if dept else request.department_id}'")
    if request.preferred_date:
        parts.append(f"available on {request.preferred_date}")
    if request.max_fee:
        parts.append(f"fee ≤ ₹{request.max_fee}")
    if request.min_rating:
        parts.append(f"rating ≥ {request.min_rating}⭐")

    query_summary = f"Top doctors matching: {', '.join(parts)}" if parts else "Top available doctors"

    return DoctorMatchResponse(
        query_summary=query_summary,
        total_matched=len(scored),
        doctors=limited
    )


def get_quick_recommendations(
    db: Session,
    department_id: int,
    limit: int = 3
) -> DoctorMatchResponse:
    """Fast top-N recommendations for a specific department."""
    return get_doctor_recommendations(
        db=db,
        request=DoctorMatchRequest(
            department_id=department_id,
            limit=limit
        )
    )
