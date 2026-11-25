from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date, timedelta
from typing import List
import logging

from app.models.all_models import (
    User, Patient, Doctor, Department, Appointment, AppointmentStatusEnum,
    Document, Notification, UserRoleEnum
)
from app.schemas.analytics import (
    AdminAnalyticsResponse,
    PlatformOverviewStats,
    DepartmentAppointmentStat,
    DoctorPerformanceStat,
    DailyAppointmentTrend,
    RevenueStats
)

logger = logging.getLogger("healthcare_platform.analytics_service")


def get_platform_overview(db: Session) -> PlatformOverviewStats:
    today = date.today()

    total_users = db.query(User).count()
    total_patients = db.query(Patient).count()
    total_doctors = db.query(Doctor).count()
    total_departments = db.query(Department).filter(Department.is_active == True).count()

    appt_q = db.query(Appointment)
    total_appointments = appt_q.count()
    total_today = appt_q.filter(Appointment.appointment_date == today).count()
    pending = appt_q.filter(Appointment.status == AppointmentStatusEnum.REQUESTED).count()
    confirmed = appt_q.filter(Appointment.status == AppointmentStatusEnum.CONFIRMED).count()
    completed = appt_q.filter(Appointment.status == AppointmentStatusEnum.COMPLETED).count()
    cancelled = appt_q.filter(Appointment.status == AppointmentStatusEnum.CANCELLED).count()

    total_docs = db.query(Document).count()
    total_notifs = db.query(Notification).count()

    return PlatformOverviewStats(
        total_users=total_users,
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_departments=total_departments,
        total_appointments=total_appointments,
        total_appointments_today=total_today,
        appointments_pending=pending,
        appointments_confirmed=confirmed,
        appointments_completed=completed,
        appointments_cancelled=cancelled,
        total_documents_uploaded=total_docs,
        total_notifications_sent=total_notifs
    )


def get_department_breakdown(db: Session) -> List[DepartmentAppointmentStat]:
    results = (
        db.query(
            Department.id,
            Department.name,
            func.count(Appointment.id).label("total")
        )
        .outerjoin(Doctor, Doctor.department_id == Department.id)
        .outerjoin(Appointment, Appointment.doctor_id == Doctor.id)
        .filter(Department.is_active == True)
        .group_by(Department.id, Department.name)
        .order_by(func.count(Appointment.id).desc())
        .all()
    )

    grand_total = sum(r.total for r in results) or 1

    return [
        DepartmentAppointmentStat(
            department_id=r.id,
            department_name=r.name,
            total_appointments=r.total,
            percentage=round((r.total / grand_total) * 100, 2)
        )
        for r in results
    ]


def get_top_doctors(db: Session, limit: int = 5) -> List[DoctorPerformanceStat]:
    doctors = (
        db.query(Doctor)
        .join(User, User.id == Doctor.user_id)
        .join(Department, Department.id == Doctor.department_id)
        .order_by(Doctor.rating.desc())
        .limit(limit)
        .all()
    )

    stats = []
    for doc in doctors:
        appt_q = db.query(Appointment).filter(Appointment.doctor_id == doc.id)
        total = appt_q.count()
        completed = appt_q.filter(Appointment.status == AppointmentStatusEnum.COMPLETED).count()
        cancelled = appt_q.filter(Appointment.status == AppointmentStatusEnum.CANCELLED).count()

        stats.append(DoctorPerformanceStat(
            doctor_id=doc.id,
            doctor_name=doc.user.full_name,
            department=doc.department.name,
            total_appointments=total,
            completed_appointments=completed,
            cancelled_appointments=cancelled,
            average_rating=float(doc.rating or 0.0),
            consultation_fee=float(doc.consultation_fee or 0.0)
        ))

    return stats


def get_daily_trends(db: Session, days: int = 7) -> List[DailyAppointmentTrend]:
    trends = []
    today = date.today()

    for i in range(days - 1, -1, -1):
        target_date = today - timedelta(days=i)
        day_q = db.query(Appointment).filter(Appointment.appointment_date == target_date)

        trends.append(DailyAppointmentTrend(
            appointment_date=target_date,
            total=day_q.count(),
            confirmed=day_q.filter(Appointment.status == AppointmentStatusEnum.CONFIRMED).count(),
            cancelled=day_q.filter(Appointment.status == AppointmentStatusEnum.CANCELLED).count(),
            completed=day_q.filter(Appointment.status == AppointmentStatusEnum.COMPLETED).count()
        ))

    return trends


def get_revenue_stats(db: Session) -> RevenueStats:
    today = date.today()
    month_start = today.replace(day=1)

    doctors = db.query(Doctor).all()
    if not doctors:
        return RevenueStats(
            total_estimated_revenue=0.0,
            revenue_this_month=0.0,
            average_consultation_fee=0.0
        )

    avg_fee = sum(float(d.consultation_fee or 0) for d in doctors) / len(doctors)

    # Estimate revenue from COMPLETED appointments
    completed = db.query(Appointment).filter(
        Appointment.status == AppointmentStatusEnum.COMPLETED
    ).all()

    total_revenue = 0.0
    for appt in completed:
        doc = db.query(Doctor).filter(Doctor.id == appt.doctor_id).first()
        if doc:
            total_revenue += float(doc.consultation_fee or 0)

    # This month
    monthly_completed = db.query(Appointment).filter(
        Appointment.status == AppointmentStatusEnum.COMPLETED,
        Appointment.appointment_date >= month_start
    ).all()

    monthly_revenue = 0.0
    for appt in monthly_completed:
        doc = db.query(Doctor).filter(Doctor.id == appt.doctor_id).first()
        if doc:
            monthly_revenue += float(doc.consultation_fee or 0)

    # Top earning doctor (most completed appointments × fee)
    top_doctor = None
    top_earnings = 0.0
    for doc in doctors:
        completed_count = db.query(Appointment).filter(
            Appointment.doctor_id == doc.id,
            Appointment.status == AppointmentStatusEnum.COMPLETED
        ).count()
        earnings = completed_count * float(doc.consultation_fee or 0)
        if earnings > top_earnings:
            top_earnings = earnings
            top_doctor = doc.user.full_name

    return RevenueStats(
        total_estimated_revenue=round(total_revenue, 2),
        revenue_this_month=round(monthly_revenue, 2),
        average_consultation_fee=round(avg_fee, 2),
        top_earning_doctor=top_doctor
    )


def get_full_analytics(db: Session) -> AdminAnalyticsResponse:
    return AdminAnalyticsResponse(
        overview=get_platform_overview(db),
        department_breakdown=get_department_breakdown(db),
        top_doctors=get_top_doctors(db),
        daily_trends=get_daily_trends(db),
        revenue=get_revenue_stats(db)
    )
