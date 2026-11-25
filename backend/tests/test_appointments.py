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


def test_appointment_booking_and_double_booking_prevention(client):
    patient_headers, _ = get_user_headers(client, "patient_book@example.com", "PATIENT", "Booking Patient")
    doctor_headers, _ = get_user_headers(client, "doctor_book@example.com", "DOCTOR", "Dr. Booking")

    # Get doctor ID & department ID
    doc_res = client.get("/api/v1/doctors?search_query=Booking")
    doctor = doc_res.json()[0]
    doctor_id = doctor["id"]
    department_id = doctor["department_id"]

    target_date = str(date.today() + timedelta(days=2))

    booking_payload = {
        "doctor_id": doctor_id,
        "department_id": department_id,
        "appointment_date": target_date,
        "start_time": "10:00:00",
        "end_time": "10:30:00",
        "appointment_type": "IN_PERSON",
        "reason_for_visit": "Regular Skin Checkup"
    }

    # 1. Successful Booking
    res1 = client.post("/api/v1/appointments", json=booking_payload, headers=patient_headers)
    assert res1.status_code == 201
    appt_data = res1.json()
    assert appt_data["status"] == "CONFIRMED"
    assert appt_data["reason_for_visit"] == "Regular Skin Checkup"
    appt_id = appt_data["id"]

    # 2. Attempt double booking same slot -> HTTP 400 Bad Request
    res2 = client.post("/api/v1/appointments", json=booking_payload, headers=patient_headers)
    assert res2.status_code == 400
    assert "already been booked" in res2.json()["detail"]

    # 3. Doctor views schedule
    doc_schedule = client.get("/api/v1/appointments", headers=doctor_headers)
    assert doc_schedule.status_code == 200
    assert len(doc_schedule.json()) == 1

    # 4. Doctor updates status to IN_PROGRESS and adds clinical note
    update_res = client.put(f"/api/v1/appointments/{appt_id}", json={
        "status": "IN_PROGRESS",
        "notes": "Patient presented with mild rash."
    }, headers=doctor_headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "IN_PROGRESS"
    assert update_res.json()["notes"] == "Patient presented with mild rash."


def test_appointment_reschedule_and_cancellation(client):
    patient_headers, _ = get_user_headers(client, "patient_resch@example.com", "PATIENT", "Resch Patient")
    doctor_headers, _ = get_user_headers(client, "doctor_resch@example.com", "DOCTOR", "Dr. Resch")

    doc_res = client.get("/api/v1/doctors?search_query=Resch")
    doctor = doc_res.json()[0]

    target_date = str(date.today() + timedelta(days=3))
    new_date = str(date.today() + timedelta(days=4))

    # 1. Book appointment
    book_res = client.post("/api/v1/appointments", json={
        "doctor_id": doctor["id"],
        "department_id": doctor["department_id"],
        "appointment_date": target_date,
        "start_time": "11:00:00",
        "end_time": "11:30:00",
        "appointment_type": "TELECONSULTATION",
        "reason_for_visit": "Fever & Cough"
    }, headers=patient_headers)
    assert book_res.status_code == 201
    appt_id = book_res.json()["id"]

    # 2. Reschedule to new date & time
    resch_res = client.post(f"/api/v1/appointments/{appt_id}/reschedule", json={
        "new_date": new_date,
        "new_start_time": "14:00:00",
        "new_end_time": "14:30:00",
        "reason": "Schedule Conflict"
    }, headers=patient_headers)
    assert resch_res.status_code == 200
    assert resch_res.json()["appointment_date"] == new_date
    assert resch_res.json()["start_time"] == "14:00:00"

    # 3. Cancel appointment
    cancel_res = client.post(f"/api/v1/appointments/{appt_id}/cancel?reason=Personal", headers=patient_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
