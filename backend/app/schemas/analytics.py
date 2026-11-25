from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class PlatformOverviewStats(BaseModel):
    total_users: int
    total_patients: int
    total_doctors: int
    total_departments: int
    total_appointments: int
    total_appointments_today: int
    appointments_pending: int  # maps to REQUESTED status
    appointments_confirmed: int
    appointments_completed: int
    appointments_cancelled: int
    total_documents_uploaded: int
    total_notifications_sent: int


class DepartmentAppointmentStat(BaseModel):
    department_id: int
    department_name: str
    total_appointments: int
    percentage: float


class DoctorPerformanceStat(BaseModel):
    doctor_id: int
    doctor_name: str
    department: str
    total_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    average_rating: float
    consultation_fee: float


class DailyAppointmentTrend(BaseModel):
    appointment_date: date
    total: int
    confirmed: int
    cancelled: int
    completed: int


class RevenueStats(BaseModel):
    total_estimated_revenue: float
    revenue_this_month: float
    average_consultation_fee: float
    top_earning_doctor: Optional[str] = None


class AdminAnalyticsResponse(BaseModel):
    overview: PlatformOverviewStats
    department_breakdown: List[DepartmentAppointmentStat]
    top_doctors: List[DoctorPerformanceStat]
    daily_trends: List[DailyAppointmentTrend]
    revenue: RevenueStats
