from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.analytics import (
    AdminAnalyticsResponse,
    PlatformOverviewStats,
    DepartmentAppointmentStat,
    DoctorPerformanceStat,
    DailyAppointmentTrend,
    RevenueStats
)
from app.services.analytics_service import (
    get_full_analytics,
    get_platform_overview,
    get_department_breakdown,
    get_top_doctors,
    get_daily_trends,
    get_revenue_stats
)
from app.api.deps import RequireRole
from app.models.all_models import User, UserRoleEnum

router = APIRouter(prefix="/analytics", tags=["Admin Analytics & Reporting"])


@router.get(
    "/dashboard",
    response_model=AdminAnalyticsResponse,
    summary="Full Admin Analytics Dashboard",
    description="Returns complete platform analytics: overview KPIs, department breakdown, top doctors, daily trends, and revenue stats. Admin only."
)
def analytics_dashboard(
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    return get_full_analytics(db)


@router.get(
    "/overview",
    response_model=PlatformOverviewStats,
    summary="Platform Overview KPIs",
    description="Returns high-level platform KPIs: user counts, appointment status breakdown, document uploads. Admin only."
)
def overview_stats(
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    return get_platform_overview(db)


@router.get(
    "/departments",
    response_model=List[DepartmentAppointmentStat],
    summary="Department Appointment Breakdown",
    description="Returns appointment counts and percentage share per department. Admin only."
)
def department_stats(
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    return get_department_breakdown(db)


@router.get(
    "/doctors",
    response_model=List[DoctorPerformanceStat],
    summary="Top Doctor Performance Report",
    description="Returns top N doctors ranked by rating with appointment and revenue stats. Admin only."
)
def doctor_stats(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    return get_top_doctors(db, limit=limit)


@router.get(
    "/trends",
    response_model=List[DailyAppointmentTrend],
    summary="Daily Appointment Trend (Last N Days)",
    description="Returns daily appointment counts (total, confirmed, cancelled, completed) for the last N days. Admin only."
)
def daily_trends(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    return get_daily_trends(db, days=days)


@router.get(
    "/revenue",
    response_model=RevenueStats,
    summary="Revenue & Earnings Report",
    description="Returns estimated platform revenue based on completed appointments and consultation fees. Admin only."
)
def revenue_stats(
    current_user: User = Depends(RequireRole([UserRoleEnum.ADMIN])),
    db: Session = Depends(get_db)
):
    return get_revenue_stats(db)
