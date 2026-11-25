"""
Phase 19: Integration Tests — End-to-End Patient & Doctor Workflow

Tests the complete lifecycle from registration through feedback,
covering cross-module interactions that unit tests miss.
"""
import io
import pytest
from datetime import date, timedelta


# ── Shared helpers ─────────────────────────────────────────────────────────────

def register(client, email, role, name):
    res = client.post("/api/v1/auth/register", json={
        "email": email, "password": "Password123",
        "full_name": name, "role": role
    })
    assert res.status_code == 201, f"Register failed: {res.json()}"
    data = res.json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data["user"]["id"]


def find_doctor(client, name_keyword):
    res = client.get(f"/api/v1/doctors?search_query={name_keyword}")
    doctors = res.json()
    assert doctors, f"No doctor found for keyword '{name_keyword}'"
    return doctors[0]


def book_appointment(client, patient_h, doctor, offset_days=10):
    target = str(date.today() + timedelta(days=offset_days))
    res = client.post("/api/v1/appointments", json={
        "doctor_id": doctor["id"],
        "department_id": doctor["department_id"],
        "appointment_date": target,
        "start_time": "10:00:00",
        "end_time": "10:30:00",
        "appointment_type": "IN_PERSON",
        "reason_for_visit": "Integration test visit"
    }, headers=patient_h)
    assert res.status_code == 201, f"Booking failed: {res.json()}"
    return res.json()


# ══════════════════════════════════════════════════════════════════════════════
# TEST 1: Full patient onboarding → AI navigation → appointment → feedback
# ══════════════════════════════════════════════════════════════════════════════

def test_full_patient_journey(client):
    """
    End-to-end: register patient → chat with AI → get recommendations
    → book appointment → receive notifications → submit feedback.
    """
    doctor_h, _ = register(client, "integ_doc_A@example.com", "DOCTOR", "IntegDocA")
    patient_h, patient_uid = register(client, "integ_patient_A@example.com", "PATIENT", "IntegPatientA")
    admin_h, _ = register(client, "integ_admin_A@example.com", "ADMIN", "IntegAdminA")

    # 1. Patient should have a welcome notification from registration
    notif_res = client.get("/api/v1/notifications", headers=patient_h)
    assert notif_res.status_code == 200
    assert notif_res.json()["total"] >= 1

    # 2. AI care navigation session — response key is 'reply'
    ai_res = client.post("/api/v1/ai/chat", json={
        "message": "I have a headache and feel dizzy, which doctor should I see?"
    }, headers=patient_h)
    assert ai_res.status_code == 200
    ai_data = ai_res.json()
    assert "conversation_id" in ai_data
    assert "reply" in ai_data
    assert len(ai_data["reply"]) > 10

    # 3. Doctor recommendations
    doctor = find_doctor(client, "IntegDocA")
    rec_res = client.post("/api/v1/recommendations/doctors", json={
        "department_id": doctor["department_id"]
    }, headers=patient_h)
    assert rec_res.status_code == 200

    # 4. Book appointment
    appt = book_appointment(client, patient_h, doctor, offset_days=12)
    appt_id = appt["id"]
    assert appt["status"] in ("CONFIRMED", "REQUESTED")

    # 5. Admin marks appointment COMPLETED
    upd = client.put(f"/api/v1/appointments/{appt_id}",
                     json={"status": "COMPLETED"}, headers=admin_h)
    assert upd.status_code == 200

    # 6. Patient submits feedback
    fb = client.post("/api/v1/feedback", json={
        "appointment_id": appt_id, "rating": 5,
        "comments": "Full journey worked perfectly!"
    }, headers=patient_h)
    assert fb.status_code == 201
    assert fb.json()["rating"] == 5


# ══════════════════════════════════════════════════════════════════════════════
# TEST 2: Document upload → list → retrieve chunks → delete lifecycle
# ══════════════════════════════════════════════════════════════════════════════

def test_document_lifecycle_integration(client):
    """Patient uploads, lists, retrieves chunks, then deletes a document."""
    patient_h, _ = register(client, "integ_doc_lifecycle@example.com", "PATIENT", "DocLifecycle")

    # Upload
    content = b"Blood pressure: 120/80 mmHg. Cholesterol: Normal. " * 20
    upload = client.post("/api/v1/documents/upload",
                         files={"file": ("report.pdf", io.BytesIO(content), "application/pdf")},
                         data={"title": "Annual Report"},
                         headers=patient_h)
    assert upload.status_code == 201
    doc_id = upload.json()["id"]
    assert upload.json()["chunk_count"] >= 1

    # List
    listing = client.get("/api/v1/documents", headers=patient_h)
    assert listing.json()["total"] >= 1

    # Detail with chunks
    detail = client.get(f"/api/v1/documents/{doc_id}", headers=patient_h)
    assert detail.status_code == 200
    assert len(detail.json()["chunks"]) >= 1

    # Delete
    delete = client.delete(f"/api/v1/documents/{doc_id}", headers=patient_h)
    assert delete.status_code == 200

    # Confirm gone
    after = client.get("/api/v1/documents", headers=patient_h)
    ids = [d["id"] for d in after.json()["documents"]]
    assert doc_id not in ids


# ══════════════════════════════════════════════════════════════════════════════
# TEST 3: Admin analytics reflects real data
# ══════════════════════════════════════════════════════════════════════════════

def test_analytics_reflects_real_data(client):
    """Register users and verify analytics overview counts update."""
    admin_h, _ = register(client, "integ_analytics_admin@example.com", "ADMIN", "AnalyticsAdmin")
    register(client, "integ_analytics_p1@example.com", "PATIENT", "AnalyticsP1")
    register(client, "integ_analytics_d1@example.com", "DOCTOR", "AnalyticsD1")

    res = client.get("/api/v1/analytics/overview", headers=admin_h)
    assert res.status_code == 200
    data = res.json()

    assert data["total_users"] >= 3
    assert data["total_patients"] >= 1
    assert data["total_doctors"] >= 1
    assert data["total_departments"] >= 1


# ══════════════════════════════════════════════════════════════════════════════
# TEST 4: Waitlist → cancellation → verify waitlist entry exists
# ══════════════════════════════════════════════════════════════════════════════

def test_waitlist_integration(client):
    """
    Patient books appointment → another patient joins waitlist →
    P1 cancels → waitlist entry is still tracked for P2.
    """
    doctor_h, _ = register(client, "integ_wait_doc@example.com", "DOCTOR", "IntegWaitDoc")
    patient1_h, _ = register(client, "integ_wait_p1@example.com", "PATIENT", "IntegWaitP1")
    patient2_h, _ = register(client, "integ_wait_p2@example.com", "PATIENT", "IntegWaitP2")

    doctor = find_doctor(client, "IntegWaitDoc")

    # P1 books appointment
    appt = book_appointment(client, patient1_h, doctor, offset_days=15)
    appt_id = appt["id"]

    # P2 joins waitlist — correct endpoint: POST /api/v1/waitlist (no /join suffix)
    wl = client.post("/api/v1/waitlist", json={
        "department_id": doctor["department_id"],
        "doctor_id": doctor["id"],
        "preferred_date": str(date.today() + timedelta(days=15)),
        "preferred_time_slot": "morning"
    }, headers=patient2_h)
    assert wl.status_code in (201, 200), f"Waitlist join failed: {wl.json()}"

    # P1 cancels
    cancel = client.post(f"/api/v1/appointments/{appt_id}/cancel?reason=Personal",
                         headers=patient1_h)
    assert cancel.status_code == 200

    # P2 waitlist entry still exists — correct endpoint: GET /api/v1/waitlist/me
    wl_list = client.get("/api/v1/waitlist/me", headers=patient2_h)
    assert wl_list.status_code == 200
    assert len(wl_list.json()) >= 1


# ══════════════════════════════════════════════════════════════════════════════
# TEST 5: RBAC — cross-role access enforcement
# ══════════════════════════════════════════════════════════════════════════════

def test_rbac_cross_role_enforcement(client):
    """Verify role boundaries are enforced across multiple protected endpoints."""
    patient_h, _ = register(client, "integ_rbac_patient@example.com", "PATIENT", "RBACPatient")
    doctor_h, _ = register(client, "integ_rbac_doctor@example.com", "DOCTOR", "RBACDoctor")

    # Patient cannot access analytics dashboard
    assert client.get("/api/v1/analytics/dashboard", headers=patient_h).status_code == 403

    # Doctor cannot access analytics dashboard
    assert client.get("/api/v1/analytics/dashboard", headers=doctor_h).status_code == 403

    # Patient cannot access audit logs
    assert client.get("/api/v1/audit", headers=patient_h).status_code == 403

    # Unauthenticated request to protected route
    assert client.get("/api/v1/notifications").status_code == 401
