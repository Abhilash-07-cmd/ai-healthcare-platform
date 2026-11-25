import pytest


def get_admin_headers(client):
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "dept_admin@example.com",
        "password": "AdminPassword123",
        "full_name": "Department Admin",
        "role": "ADMIN"
    })
    token = reg_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_list_seeded_departments(client):
    res = client.get("/api/v1/departments")
    assert res.status_code == 200
    departments = res.json()
    assert len(departments) >= 6
    codes = [d["code"] for d in departments]
    assert "DERM" in codes
    assert "CARD" in codes
    assert "GEN_MED" in codes


def test_create_department_admin_only(client):
    admin_headers = get_admin_headers(client)

    # 1. Create department as Admin
    dept_payload = {
        "name": "Oncology",
        "code": "ONCO",
        "description": "Cancer treatment and oncology consultations",
        "icon": "ribbon"
    }
    create_res = client.post("/api/v1/departments", json=dept_payload, headers=admin_headers)
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["name"] == "Oncology"
    assert data["code"] == "ONCO"

    # 2. Duplicate creation fails -> 400
    dup_res = client.post("/api/v1/departments", json=dept_payload, headers=admin_headers)
    assert dup_res.status_code == 400


def test_update_and_deactivate_department(client):
    admin_headers = get_admin_headers(client)

    # List departments to get one ID
    list_res = client.get("/api/v1/departments")
    derm_dept = next(d for d in list_res.json() if d["code"] == "DERM")
    dept_id = derm_dept["id"]

    # Update description
    update_res = client.put(f"/api/v1/departments/{dept_id}", json={
        "description": "Updated dermatology description"
    }, headers=admin_headers)
    assert update_res.status_code == 200
    assert update_res.json()["description"] == "Updated dermatology description"

    # Deactivate department
    del_res = client.delete(f"/api/v1/departments/{dept_id}", headers=admin_headers)
    assert del_res.status_code == 200

    # Verify inactive department omitted from public list
    list_after = client.get("/api/v1/departments")
    active_codes = [d["code"] for d in list_after.json()]
    assert "DERM" not in active_codes
