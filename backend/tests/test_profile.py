def test_profile_requires_applicant_type(client) -> None:
    response = client.post("/api/profile", json={"state": "Maharashtra"})
    assert response.status_code == 422


def test_profile_rejects_invalid_type(client) -> None:
    response = client.post("/api/profile", json={"applicant_type": "enterprise"})
    assert response.status_code == 422


def test_create_and_read_individual_profile(client) -> None:
    response = client.post(
        "/api/profile",
        json={
            "applicant_type": "individual",
            "age": 28,
            "state": "Maharashtra",
            "income": 200000,
            "occupation": "salaried",
        },
    )
    assert response.status_code == 200
    profile = response.json()["data"]
    assert profile["applicant_type"] == "individual"
    fetched = client.get(f"/api/profile/{profile['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["data"]["income"] == 200000


def test_create_small_business_profile(client) -> None:
    response = client.post(
        "/api/profile",
        json={
            "applicant_type": "small_business",
            "state": "Maharashtra",
            "turnover": 5000000,
            "registration_status": "registered",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["applicant_type"] == "small_business"
