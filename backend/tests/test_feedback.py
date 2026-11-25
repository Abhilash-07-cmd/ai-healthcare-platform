import pytest
from datetime import date, timedelta


# ── Helpers ───────────────────────────────────────────────────────────────────

def register_and_login(client, email, role, full_name):
    res = client.post("/api/v1/auth/register", json={
        "email": email, "password": "Password123",
        "full_name": full_name, "role": role
    })
    assert res.status_code == 201
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def seed_completed_appointment(client, patient_headers, doctor_name_keyword):
    """
    Look up a registered doctor by name, book an appointment, then
    mark it COMPLETED via admin. Returns (appointment_id, doctor_id).
    """
    # Look up the doctor via search
    doc_res = client.get(f"/api/v1/doctors?search_query={doctor_name_keyword}")
    doctors = doc_res.json()
    if not doctors:
        pytest.skip(f"No doctor matching '{doctor_name_keyword}' found")
    doctor = doctors[0]
    doctor_id = doctor["id"]
    dept_id = doctor["department_id"]

    target_date = str(date.today() + timedelta(days=5))

    # Book appointment
    appt_res = client.post("/api/v1/appointments", json={
        "doctor_id": doctor_id,
        "department_id": dept_id,
        "appointment_date": target_date,
        "start_time": "09:00:00",
        "end_time": "09:30:00",
        "appointment_type": "IN_PERSON",
        "reason_for_visit": "Routine checkup for feedback test"
    }, headers=patient_headers)
    assert appt_res.status_code == 201, f"Booking failed: {appt_res.json()}"
    appt_id = appt_res.json()["id"]

    # Mark as COMPLETED via admin
    admin_headers = register_and_login(client, f"fb_admin_{appt_id}@example.com", "ADMIN", "FB Admin")
    update_res = client.put(f"/api/v1/appointments/{appt_id}",
                            json={"status": "COMPLETED"}, headers=admin_headers)
    assert update_res.status_code == 200, f"Status update failed: {update_res.json()}"

    return appt_id, doctor_id


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_submit_feedback_for_completed_appointment(client):
    register_and_login(client, "fb_doctor1@example.com", "DOCTOR", "FbDoctorOne")
    patient_h = register_and_login(client, "fb_patient1@example.com", "PATIENT", "FB Patient One")

    appt_id, doctor_id = seed_completed_appointment(client, patient_h, "FbDoctorOne")

    res = client.post("/api/v1/feedback", json={
        "appointment_id": appt_id,
        "rating": 5,
        "comments": "Excellent doctor, very thorough!"
    }, headers=patient_h)

    assert res.status_code == 201
    data = res.json()
    assert data["rating"] == 5
    assert data["appointment_id"] == appt_id
    assert "Excellent" in data["comments"]


def test_duplicate_feedback_rejected(client):
    register_and_login(client, "fb_doctor2@example.com", "DOCTOR", "FbDoctorTwo")
    patient_h = register_and_login(client, "fb_patient2@example.com", "PATIENT", "FB Patient Two")

    appt_id, _ = seed_completed_appointment(client, patient_h, "FbDoctorTwo")

    # First submission
    r1 = client.post("/api/v1/feedback", json={
        "appointment_id": appt_id, "rating": 4, "comments": "Good"
    }, headers=patient_h)
    assert r1.status_code == 201

    # Duplicate — same appointment
    r2 = client.post("/api/v1/feedback", json={
        "appointment_id": appt_id, "rating": 3, "comments": "Changed my mind"
    }, headers=patient_h)
    assert r2.status_code == 409


def test_feedback_updates_doctor_rating(client):
    register_and_login(client, "fb_doctor3@example.com", "DOCTOR", "FbDoctorThree")
    patient_h = register_and_login(client, "fb_patient3@example.com", "PATIENT", "FB Patient Three")

    appt_id, doctor_id = seed_completed_appointment(client, patient_h, "FbDoctorThree")

    client.post("/api/v1/feedback", json={
        "appointment_id": appt_id, "rating": 4, "comments": "Pretty good"
    }, headers=patient_h)

    summary_res = client.get(f"/api/v1/feedback/doctor/{doctor_id}/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_reviews"] >= 1
    assert summary["average_rating"] > 0
    assert "rating_breakdown" in summary


def test_my_feedbacks_list(client):
    register_and_login(client, "fb_doctor4@example.com", "DOCTOR", "FbDoctorFour")
    patient_h = register_and_login(client, "fb_patient4@example.com", "PATIENT", "FB Patient Four")

    appt_id, _ = seed_completed_appointment(client, patient_h, "FbDoctorFour")

    client.post("/api/v1/feedback", json={
        "appointment_id": appt_id, "rating": 3, "comments": "Average experience"
    }, headers=patient_h)

    res = client.get("/api/v1/feedback/me", headers=patient_h)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert isinstance(data["average_rating"], float)


def test_doctor_public_reviews_accessible(client):
    register_and_login(client, "fb_doctor5@example.com", "DOCTOR", "FbDoctorFive")
    patient_h = register_and_login(client, "fb_patient5@example.com", "PATIENT", "FB Patient Five")

    appt_id, doctor_id = seed_completed_appointment(client, patient_h, "FbDoctorFive")

    client.post("/api/v1/feedback", json={
        "appointment_id": appt_id, "rating": 5, "comments": "Outstanding!"
    }, headers=patient_h)

    # No auth needed
    res = client.get(f"/api/v1/feedback/doctor/{doctor_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any(f["comments"] == "Outstanding!" for f in data["feedbacks"])
