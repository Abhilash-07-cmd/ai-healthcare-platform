import pytest


def get_user_headers(client, email, role, name):
    res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123",
        "full_name": name,
        "role": role
    })
    assert res.status_code == 201
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_registration_creates_welcome_notification(client):
    headers = get_user_headers(client, "notif_patient@example.com", "PATIENT", "Notif Patient")

    res = client.get("/api/v1/notifications", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    types = [n["notification_type"] for n in data["notifications"]]
    assert "WELCOME" in types


def test_unread_count_returns_badge_number(client):
    headers = get_user_headers(client, "notif_count@example.com", "PATIENT", "Count Patient")

    res = client.get("/api/v1/notifications/count", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "unread_count" in data
    assert data["unread_count"] >= 1


def test_mark_single_notification_as_read(client):
    headers = get_user_headers(client, "notif_read@example.com", "PATIENT", "Read Patient")

    # Get first notification
    list_res = client.get("/api/v1/notifications", headers=headers)
    notifications = list_res.json()["notifications"]
    assert len(notifications) > 0
    notif_id = notifications[0]["id"]

    # Mark it as read
    mark_res = client.put("/api/v1/notifications/read", json={
        "notification_ids": [notif_id]
    }, headers=headers)
    assert mark_res.status_code == 200
    assert mark_res.json()["updated_count"] >= 1

    # Verify it's now read
    list_res2 = client.get("/api/v1/notifications", headers=headers)
    updated = next((n for n in list_res2.json()["notifications"] if n["id"] == notif_id), None)
    assert updated is not None
    assert updated["is_read"] is True


def test_mark_all_notifications_as_read(client):
    headers = get_user_headers(client, "notif_all@example.com", "PATIENT", "All Read Patient")

    # Mark all as read
    res = client.put("/api/v1/notifications/read-all", headers=headers)
    assert res.status_code == 200

    # Verify unread count is now 0
    count_res = client.get("/api/v1/notifications/count", headers=headers)
    assert count_res.json()["unread_count"] == 0

    # Unread-only filter should return empty list
    unread_res = client.get("/api/v1/notifications?unread_only=true", headers=headers)
    assert unread_res.json()["notifications"] == []


def test_delete_single_notification(client):
    headers = get_user_headers(client, "notif_del@example.com", "PATIENT", "Delete Patient")

    # Get first notification id
    list_res = client.get("/api/v1/notifications", headers=headers)
    notif_id = list_res.json()["notifications"][0]["id"]
    total_before = list_res.json()["total"]

    # Delete it
    del_res = client.delete(f"/api/v1/notifications/{notif_id}", headers=headers)
    assert del_res.status_code == 200

    # Confirm total decreased
    list_res2 = client.get("/api/v1/notifications", headers=headers)
    assert list_res2.json()["total"] == total_before - 1


def test_clear_read_notifications(client):
    headers = get_user_headers(client, "notif_clear@example.com", "PATIENT", "Clear Patient")

    # First mark all as read
    client.put("/api/v1/notifications/read-all", headers=headers)

    # Now clear all read
    clear_res = client.delete("/api/v1/notifications/clear-read", headers=headers)
    assert clear_res.status_code == 200
    assert clear_res.json()["deleted_count"] >= 1

    # Notification list should now be empty
    list_res = client.get("/api/v1/notifications", headers=headers)
    assert list_res.json()["total"] == 0
