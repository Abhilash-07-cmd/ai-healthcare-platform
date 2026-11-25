import pytest


def get_auth_header(client, email: str, password: str, role: str, name: str):
    reg_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": name,
        "role": role
    })
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_patient_profile_update(client):
    headers = get_auth_header(client, "patient_prof@example.com", "Password123", "PATIENT", "Patient Test")

    # Get initial profile
    res1 = client.get("/api/v1/patients/me", headers=headers)
    assert res1.status_code == 200
    assert res1.json()["user"]["full_name"] == "Patient Test"

    # Update profile
    update_payload = {
        "date_of_birth": "1995-05-15",
        "gender": "Female",
        "blood_group": "O+",
        "emergency_contact": "+1999888777",
        "medical_history_summary": "No allergies",
        "full_name": "Jane Updated Patient"
    }
    res2 = client.put("/api/v1/patients/me", json=update_payload, headers=headers)
    assert res2.status_code == 200
    data = res2.json()
    assert data["date_of_birth"] == "1995-05-15"
    assert data["gender"] == "Female"
    assert data["blood_group"] == "O+"
    assert data["user"]["full_name"] == "Jane Updated Patient"


def test_doctor_profile_update_and_public_search(client):
    headers = get_auth_header(client, "doctor_prof@example.com", "Password123", "DOCTOR", "Dr. Alice")

    # Update doctor profile
    update_payload = {
        "qualification": "MD Cardiology",
        "experience_years": 12,
        "bio": "Experienced cardiologist specializing in heart health.",
        "consultation_fee": 1000.0,
        "is_available": True
    }
    res1 = client.put("/api/v1/doctors/me", json=update_payload, headers=headers)
    assert res1.status_code == 200
    data = res1.json()
    assert data["qualification"] == "MD Cardiology"
    assert data["experience_years"] == 12

    # Public doctor search
    search_res = client.get("/api/v1/doctors?search_query=Alice")
    assert search_res.status_code == 200
    doctors = search_res.json()
    assert len(doctors) == 1
    assert doctors[0]["user"]["full_name"] == "Dr. Alice"


def test_admin_user_management(client):
    admin_headers = get_auth_header(client, "admin_prof@example.com", "AdminPassword123", "ADMIN", "Admin User")
    patient_headers = get_auth_header(client, "sub_patient_prof@example.com", "Password123", "PATIENT", "Sub Patient")

    # Patient trying to access admin endpoint -> 403
    forbidden_res = client.get("/api/v1/admin/users", headers=patient_headers)
    assert forbidden_res.status_code == 403

    # Admin listing users -> 200
    users_res = client.get("/api/v1/admin/users", headers=admin_headers)
    assert users_res.status_code == 200
    users = users_res.json()
    assert len(users) >= 2

    # Audit logs
    audit_res = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) >= 2
