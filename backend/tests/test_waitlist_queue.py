import pytest
from datetime import date, timedelta


def get_user_headers(client, email: str, role: str, name: str):
    reg_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123",
        "full_name": name,
        "role": role
    })
    token = reg_res.json()["access_token"]
    user_id = reg_res.json()["user"]["id"]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_waitlist_lifecycle_and_cancellation_trigger(client):
    patient1_headers, _ = get_user_headers(client, "patient_w1@example.com", "PATIENT", "Waitlist Patient 1")
    patient2_headers, _ = get_user_headers(client, "patient_w2@example.com", "PATIENT", "Waitlist Patient 2")
    doctor_headers, _ = get_user_headers(client, "doctor_w@example.com", "DOCTOR", "Dr. Waitlist")

    # Get doctor & department
    doc_res = client.get("/api/v1/doctors?search_query=Waitlist")
    doctor = doc_res.json()[0]
    doctor_id = doctor["id"]
    department_id = doctor["department_id"]

    target_date = str(date.today() + timedelta(days=5))

    # 1. Patient 1 books appointment
    book_res = client.post("/api/v1/appointments", json={
        "doctor_id": doctor_id,
        "department_id": department_id,
        "appointment_date": target_date,
        "start_time": "10:00:00",
        "end_time": "10:30:00",
        "reason_for_visit": "Consultation"
    }, headers=patient1_headers)
    assert book_res.status_code == 201
    appt_id = book_res.json()["id"]

    # 2. Patient 2 joins waitlist for same date -> Position #1
    w_res1 = client.post("/api/v1/waitlist", json={
        "department_id": department_id,
        "doctor_id": doctor_id,
        "preferred_date": target_date,
        "preferred_time_slot": "morning"
    }, headers=patient2_headers)
    assert w_res1.status_code == 201
    w_entry = w_res1.json()
    assert w_entry["position"] == 1
    assert w_entry["status"] == "WAITING"

    # 3. Patient 1 cancels appointment -> Triggers waitlist notification for Patient 2
    cancel_res = client.post(f"/api/v1/appointments/{appt_id}/cancel", headers=patient1_headers)
    assert cancel_res.status_code == 200

    # 4. Verify Patient 2 waitlist status updated to NOTIFIED
    my_waitlist = client.get("/api/v1/waitlist/me", headers=patient2_headers)
    assert my_waitlist.status_code == 200
    entries = my_waitlist.json()
    assert len(entries) == 1
    assert entries[0]["status"] in ["WAITING", "NOTIFIED"]

    # 5. Patient 2 accepts waitlist slot -> converts to appointment
    accept_res = client.post(f"/api/v1/waitlist/{w_entry['id']}/accept", json={
        "start_time": "10:00:00",
        "end_time": "10:30:00"
    }, headers=patient2_headers)
    assert accept_res.status_code == 200
    assert "appointment_id" in accept_res.json()


def test_live_clinic_queue(client):
    patient_headers, _ = get_user_headers(client, "patient_q@example.com", "PATIENT", "Queue Patient")
    doctor_headers, _ = get_user_headers(client, "doctor_q@example.com", "DOCTOR", "Dr. Queue")

    doc_res = client.get("/api/v1/doctors?search_query=Queue")
    doctor = doc_res.json()[0]
    doctor_id = doctor["id"]

    today_date = str(date.today())

    # Book 2 appointments for today
    client.post("/api/v1/appointments", json={
        "doctor_id": doctor_id,
        "department_id": doctor["department_id"],
        "appointment_date": today_date,
        "start_time": "09:00:00",
        "end_time": "09:30:00"
    }, headers=patient_headers)

    # Query live queue
    q_res = client.get(f"/api/v1/queue/live?doctor_id={doctor_id}")
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["doctor_id"] == doctor_id
    assert "estimated_waiting_time_minutes" in q_data
    assert "disclaimer" in q_data
