import io
import pytest


def get_patient_headers(client, email="doc_patient@example.com"):
    res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123",
        "full_name": "Doc Test Patient",
        "role": "PATIENT"
    })
    assert res.status_code == 201
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def make_fake_pdf(content: str = "Patient report: Normal ECG. No abnormalities detected.") -> tuple:
    """Return a (filename, file-like-object, content-type) tuple simulating a PDF."""
    return ("report.pdf", io.BytesIO(content.encode("utf-8")), "application/pdf")


def test_document_upload_success(client):
    headers = get_patient_headers(client, "doc_upload@example.com")

    fname, fobj, ctype = make_fake_pdf()
    res = client.post(
        "/api/v1/documents/upload",
        files={"file": (fname, fobj, ctype)},
        data={"title": "My ECG Report"},
        headers=headers
    )

    assert res.status_code == 201
    data = res.json()
    assert data["id"] > 0
    assert data["title"] == "My ECG Report"
    assert data["file_type"] == "PDF"
    assert data["status"] == "READY"
    assert data["chunk_count"] >= 1


def test_document_upload_invalid_type_rejected(client):
    headers = get_patient_headers(client, "doc_invalid@example.com")

    res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("malware.exe", io.BytesIO(b"binary-content"), "application/octet-stream")},
        data={"title": "Bad file"},
        headers=headers
    )

    assert res.status_code == 400
    assert "not allowed" in res.json()["detail"].lower()


def test_list_documents_returns_uploaded_file(client):
    headers = get_patient_headers(client, "doc_list@example.com")

    # Upload first
    fname, fobj, ctype = make_fake_pdf("Blood test results: HbA1c normal.")
    client.post(
        "/api/v1/documents/upload",
        files={"file": (fname, fobj, ctype)},
        data={"title": "Blood Test Report"},
        headers=headers
    )

    # List
    res = client.get("/api/v1/documents", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    titles = [d["title"] for d in data["documents"]]
    assert "Blood Test Report" in titles


def test_get_document_detail_with_chunks(client):
    headers = get_patient_headers(client, "doc_detail@example.com")

    fname, fobj, ctype = make_fake_pdf("X-Ray report: Chest clear. " * 20)
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": (fname, fobj, ctype)},
        data={"title": "X-Ray Report"},
        headers=headers
    )
    doc_id = upload_res.json()["id"]

    # Get detail
    res = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == doc_id
    assert len(data["chunks"]) >= 1
    assert data["chunks"][0]["chroma_id"].startswith(f"doc_{doc_id}_chunk_0")


def test_delete_document_removes_from_list(client):
    headers = get_patient_headers(client, "doc_delete@example.com")

    fname, fobj, ctype = make_fake_pdf("MRI report: No lesions detected.")
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": (fname, fobj, ctype)},
        data={"title": "MRI Report"},
        headers=headers
    )
    doc_id = upload_res.json()["id"]

    # Delete
    del_res = client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
    assert del_res.status_code == 200
    assert "deleted" in del_res.json()["message"].lower()

    # Confirm gone
    list_res = client.get("/api/v1/documents", headers=headers)
    ids = [d["id"] for d in list_res.json()["documents"]]
    assert doc_id not in ids
