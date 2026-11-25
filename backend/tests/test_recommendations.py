import pytest
from datetime import date, timedelta


def get_user_headers(client, email, role, name):
    res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123",
        "full_name": name,
        "role": role
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_first_department_id(client, patient_headers):
    """Helper: returns the first active department's id."""
    res = client.get("/api/v1/departments", headers=patient_headers)
    return res.json()[0]["id"]


def test_recommendation_returns_scored_doctors(client):
    patient_headers = get_user_headers(client, "rec_patient@example.com", "PATIENT", "Rec Patient")
    dept_id = get_first_department_id(client, patient_headers)

    res = client.post("/api/v1/recommendations/doctors", json={
        "department_id": dept_id
    }, headers=patient_headers)

    assert res.status_code == 200
    data = res.json()
    assert "query_summary" in data
    assert "total_matched" in data
    assert isinstance(data["doctors"], list)

    if data["doctors"]:
        first = data["doctors"][0]
        assert "match_score" in first
        assert 0 <= first["match_score"] <= 100
        assert isinstance(first["match_reasons"], list)
        assert len(first["match_reasons"]) > 0


def test_recommendation_sorted_by_match_score(client):
    patient_headers = get_user_headers(client, "rec_sort@example.com", "PATIENT", "Sort Patient")
    dept_id = get_first_department_id(client, patient_headers)

    res = client.post("/api/v1/recommendations/doctors", json={
        "department_id": dept_id,
        "limit": 10
    }, headers=patient_headers)

    assert res.status_code == 200
    doctors = res.json()["doctors"]

    # Verify sorted descending by match_score
    scores = [d["match_score"] for d in doctors]
    assert scores == sorted(scores, reverse=True)


def test_recommendation_fee_filter_excludes_expensive_doctors(client):
    patient_headers = get_user_headers(client, "rec_fee@example.com", "PATIENT", "Fee Patient")

    # Use max_fee=0 to ensure no doctors pass the fee filter
    res = client.post("/api/v1/recommendations/doctors", json={
        "max_fee": 0.0
    }, headers=patient_headers)

    assert res.status_code == 200
    data = res.json()
    # All doctors should be excluded since fee > 0
    assert data["total_matched"] == 0
    assert len(data["doctors"]) == 0


def test_recommendation_min_rating_filter(client):
    patient_headers = get_user_headers(client, "rec_rating@example.com", "PATIENT", "Rating Patient")

    res = client.post("/api/v1/recommendations/doctors", json={
        "min_rating": 4.9
    }, headers=patient_headers)

    assert res.status_code == 200
    data = res.json()
    # All returned doctors must have rating >= 4.9
    for doc in data["doctors"]:
        assert doc["rating"] >= 4.9


def test_quick_recommendations_endpoint(client):
    patient_headers = get_user_headers(client, "rec_quick@example.com", "PATIENT", "Quick Patient")
    dept_id = get_first_department_id(client, patient_headers)

    res = client.get(f"/api/v1/recommendations/doctors/quick?department_id={dept_id}&limit=3",
                     headers=patient_headers)

    assert res.status_code == 200
    data = res.json()
    assert len(data["doctors"]) <= 3
    assert data["total_matched"] >= 0


def test_recommendation_match_reasons_are_human_readable(client):
    patient_headers = get_user_headers(client, "rec_reasons@example.com", "PATIENT", "Reasons Patient")
    dept_id = get_first_department_id(client, patient_headers)

    res = client.post("/api/v1/recommendations/doctors", json={
        "department_id": dept_id,
        "preferred_date": str(date.today() + timedelta(days=3))
    }, headers=patient_headers)

    assert res.status_code == 200
    doctors = res.json()["doctors"]

    for doc in doctors:
        for reason in doc["match_reasons"]:
            assert isinstance(reason, str)
            assert len(reason) > 3  # Not empty
