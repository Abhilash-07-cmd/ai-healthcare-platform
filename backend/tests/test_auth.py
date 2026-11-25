import pytest

def test_patient_registration_and_login(client):
    # 1. Register Patient
    reg_payload = {
        "email": "patient_auth@example.com",
        "password": "SecretPassword123",
        "full_name": "Jane Patient",
        "phone": "+1234567890",
        "role": "PATIENT"
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "patient_auth@example.com"
    assert data["user"]["role"] == "PATIENT"

    # 2. Login Patient
    login_payload = {
        "email": "patient_auth@example.com",
        "password": "SecretPassword123"
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    access_token = token_data["access_token"]

    # 3. Get /me Profile
    headers = {"Authorization": f"Bearer {access_token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    user_info = me_res.json()
    assert user_info["email"] == "patient_auth@example.com"
    assert user_info["full_name"] == "Jane Patient"


def test_doctor_registration_initializes_profile(client):
    reg_payload = {
        "email": "doctor_auth@example.com",
        "password": "DoctorPassword123",
        "full_name": "Dr. John Smith",
        "phone": "+1987654321",
        "role": "DOCTOR"
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["role"] == "DOCTOR"


def test_invalid_login_credentials(client):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword"
    }
    res = client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]


def test_duplicate_registration_fails(client):
    reg_payload = {
        "email": "dup@example.com",
        "password": "Password123",
        "full_name": "Duplicate User",
        "role": "PATIENT"
    }
    res1 = client.post("/api/v1/auth/register", json=reg_payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=reg_payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_refresh_token_endpoint(client):
    reg_payload = {
        "email": "refresh@example.com",
        "password": "Password123",
        "full_name": "Refresh User",
        "role": "PATIENT"
    }
    res = client.post("/api/v1/auth/register", json=reg_payload)
    refresh_token = res.json()["refresh_token"]

    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
