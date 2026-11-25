import pytest
from datetime import date, timedelta


def get_doctor_headers(client, email="doctor_avail@example.com"):
    reg_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "DoctorPassword123",
        "full_name": "Dr. Availability Tester",
        "role": "DOCTOR"
    })
    token = reg_res.json()["access_token"]
    user_id = reg_res.json()["user"]["id"]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_doctor_working_hours_configuration(client):
    headers, _ = get_doctor_headers(client)

    # 1. Set working schedule (Monday & Tuesday 09:00 to 11:00)
    avail_payload = {
        "availability": [
            {"day_of_week": 0, "start_time": "09:00:00", "end_time": "11:00:00", "slot_duration_minutes": 30},
            {"day_of_week": 1, "start_time": "09:00:00", "end_time": "11:00:00", "slot_duration_minutes": 30}
        ]
    }
    set_res = client.post("/api/v1/doctors/me/availability", json=avail_payload, headers=headers)
    assert set_res.status_code == 200
    data = set_res.json()
    assert len(data) == 2
    assert data[0]["day_of_week"] == 0

    # 2. Get availability
    get_res = client.get("/api/v1/doctors/me/availability", headers=headers)
    assert get_res.status_code == 200
    assert len(get_res.json()) == 2


def test_slot_generation_and_leave_exclusion(client):
    headers, _ = get_doctor_headers(client, email="doctor_leave_test@example.com")

    # Get doctor ID from public search
    doc_res = client.get("/api/v1/doctors?search_query=Tester")
    doctor_id = doc_res.json()[0]["id"]

    # 1. Set leave for next Monday
    today = date.today()
    # Find next Monday date
    next_monday = today + timedelta(days=(7 - today.weekday()) % 7 if today.weekday() != 0 else 7)

    leave_payload = {
        "start_date": str(next_monday),
        "end_date": str(next_monday),
        "reason": "Conference Leave"
    }
    leave_res = client.post("/api/v1/doctors/me/leave", json=leave_payload, headers=headers)
    assert leave_res.status_code == 201

    # 2. Trigger slot generation for next Monday
    gen_res = client.post(
        f"/api/v1/doctors/{doctor_id}/generate-slots",
        json={"start_date": str(next_monday), "end_date": str(next_monday)},
        headers=headers
    )
    assert gen_res.status_code == 200
    # Because doctor is on leave, 0 slots created
    assert gen_res.json()["slots_created"] == 0

    # 3. Query slots on next Tuesday (not on leave)
    next_tuesday = next_monday + timedelta(days=1)
    slots_res = client.get(f"/api/v1/doctors/{doctor_id}/slots?target_date={next_tuesday}")
    assert slots_res.status_code == 200
    slots = slots_res.json()
    assert len(slots) > 0
    assert slots[0]["slot_date"] == str(next_tuesday)
    assert slots[0]["is_booked"] == False
