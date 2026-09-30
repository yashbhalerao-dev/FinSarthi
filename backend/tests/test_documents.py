import json


def test_upload_and_process_demo_document(client) -> None:
    created = client.post(
        "/api/profile",
        json={"applicant_type": "individual", "state": "Maharashtra"},
    )
    profile_id = created.json()["data"]["id"]
    payload = json.dumps(
        {
            "document_type": "income_certificate",
            "confidence": 0.91,
            "extracted_fields": {"income": 180000, "state": "Maharashtra", "age": 30},
        }
    ).encode("utf-8")
    upload = client.post(
        "/api/documents/upload",
        data={"profile_id": profile_id},
        files={"file": ("demo-a-note.json", payload, "application/json")},
    )
    assert upload.status_code == 200
    document_id = upload.json()["data"]["id"]
    assert upload.json()["data"]["extraction_status"] == "pending"

    processed = client.post("/api/documents/process", json={"document_id": document_id})
    assert processed.status_code == 200
    body = processed.json()["data"]
    assert body["document"]["extraction_status"] == "processed"
    assert body["document"]["extracted_fields"]["income"] == 180000
    assert body["document"]["confidence"] >= 0.9
    assert body["profile"]["income"] == 180000

    listed = client.get(f"/api/documents?profile_id={profile_id}")
    assert listed.status_code == 200
    assert any(item["id"] == document_id for item in listed.json()["data"])
