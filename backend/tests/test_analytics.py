import pytest


def get_admin_headers(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "analytics_admin@example.com",
        "password": "Password123",
        "full_name": "Analytics Admin",
        "role": "ADMIN"
    })
    assert res.status_code == 201
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def get_patient_headers(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "analytics_patient@example.com",
        "password": "Password123",
        "full_name": "Analytics Patient",
        "role": "PATIENT"
    })
    assert res.status_code == 201
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_analytics_dashboard_admin_only(client):
    admin_headers = get_admin_headers(client)

    res = client.get("/api/v1/analytics/dashboard", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "overview" in data
    assert "department_breakdown" in data
    assert "top_doctors" in data
    assert "daily_trends" in data
    assert "revenue" in data


def test_analytics_dashboard_forbidden_for_patient(client):
    patient_headers = get_patient_headers(client)

    res = client.get("/api/v1/analytics/dashboard", headers=patient_headers)
    assert res.status_code == 403


def test_platform_overview_returns_correct_structure(client):
    admin_headers = get_admin_headers(client)

    res = client.get("/api/v1/analytics/overview", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()

    required_keys = [
        "total_users", "total_patients", "total_doctors",
        "total_departments", "total_appointments",
        "appointments_pending", "appointments_confirmed",
        "appointments_completed", "appointments_cancelled"
    ]
    for key in required_keys:
        assert key in data
        assert isinstance(data[key], int)


def test_department_breakdown_returns_percentages(client):
    admin_headers = get_admin_headers(client)

    res = client.get("/api/v1/analytics/departments", headers=admin_headers)
    assert res.status_code == 200
    departments = res.json()
    assert isinstance(departments, list)
    assert len(departments) >= 1

    for dept in departments:
        assert "department_name" in dept
        assert "total_appointments" in dept
        assert "percentage" in dept
        assert 0.0 <= dept["percentage"] <= 100.0


def test_daily_trends_returns_correct_days(client):
    admin_headers = get_admin_headers(client)

    res = client.get("/api/v1/analytics/trends?days=7", headers=admin_headers)
    assert res.status_code == 200
    trends = res.json()
    assert len(trends) == 7

    for trend in trends:
        assert "appointment_date" in trend
        assert "total" in trend
        assert "confirmed" in trend
        assert "cancelled" in trend
        assert "completed" in trend


def test_revenue_stats_structure(client):
    admin_headers = get_admin_headers(client)

    res = client.get("/api/v1/analytics/revenue", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()

    assert "total_estimated_revenue" in data
    assert "revenue_this_month" in data
    assert "average_consultation_fee" in data
    assert isinstance(data["total_estimated_revenue"], float)


def test_top_doctors_returns_ranked_list(client):
    admin_headers = get_admin_headers(client)

    res = client.get("/api/v1/analytics/doctors?limit=5", headers=admin_headers)
    assert res.status_code == 200
    doctors = res.json()
    assert isinstance(doctors, list)

    for doc in doctors:
        assert "doctor_name" in doc
        assert "department" in doc
        assert "average_rating" in doc
        assert "consultation_fee" in doc
