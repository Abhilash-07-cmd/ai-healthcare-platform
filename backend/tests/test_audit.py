def get_admin_headers(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "audit_admin@example.com", "password": "Password123",
        "full_name": "Audit Admin", "role": "ADMIN"
    })
    assert res.status_code == 201
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_audit_logs_endpoint_accessible_by_admin(client):
    admin_h = get_admin_headers(client)

    # Trigger a mutating action to generate an audit log
    client.post("/api/v1/departments", json={
        "name": "AuditTestDept", "code": "AUDT", "description": "Audit test dept"
    }, headers=admin_h)

    res = client.get("/api/v1/audit", headers=admin_h)
    assert res.status_code == 200
    logs = res.json()
    assert isinstance(logs, list)


def test_audit_logs_forbidden_for_non_admin(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "audit_patient@example.com", "password": "Password123",
        "full_name": "Audit Patient", "role": "PATIENT"
    })
    patient_h = {"Authorization": f"Bearer {res.json()['access_token']}"}

    res = client.get("/api/v1/audit", headers=patient_h)
    assert res.status_code == 403


def test_audit_stats_returns_action_counts(client):
    admin_h = get_admin_headers(client)

    res = client.get("/api/v1/audit/stats", headers=admin_h)
    assert res.status_code == 200
    data = res.json()
    assert "action_counts" in data
    assert isinstance(data["action_counts"], dict)
