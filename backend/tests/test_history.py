def test_history_requires_auth(client):
    response = client.get("/api/v1/history")
    assert response.status_code == 403 or response.status_code == 401

def test_save_report_on_predict(client):
    # Register and login
    client.post("/auth/register", json={
        "email": "history1@example.com",
        "password": "password123",
        "full_name": "History User 1"
    })
    login_resp = client.post("/auth/login", json={
        "email": "history1@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    
    # Analyze with auth
    analyze_resp = client.post(
        "/analyze",
        json={
            "field_id": 1,
            "nitrogen": 45.0,
            "phosphorus": 35.0,
            "potassium": 25.0,
            "ph": 7.0
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert analyze_resp.status_code == 200
    assert "history_id" in analyze_resp.json()

    # Get history
    history_resp = client.get(
        "/api/v1/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert history_resp.status_code == 200
    data = history_resp.json()
    assert data["total"] == 1
    assert data["items"][0]["nitrogen"] == 45.0

def test_get_history_forbidden(client):
    # Register user A
    client.post("/auth/register", json={
        "email": "history2@example.com",
        "password": "password123"
    })
    login_a = client.post("/auth/login", json={
        "email": "history2@example.com",
        "password": "password123"
    })
    token_a = login_a.json()["access_token"]

    # Register user B
    client.post("/auth/register", json={
        "email": "history3@example.com",
        "password": "password123"
    })
    login_b = client.post("/auth/login", json={
        "email": "history3@example.com",
        "password": "password123"
    })
    token_b = login_b.json()["access_token"]

    # User A creates a report
    analyze_resp = client.post(
        "/analyze",
        json={"field_id": 1, "nitrogen": 45.0, "phosphorus": 35.0, "potassium": 25.0, "ph": 7.0},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    report_id = analyze_resp.json()["history_id"]

    # User B tries to read User A's report
    forbidden_resp = client.get(
        f"/api/v1/history/{report_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert forbidden_resp.status_code == 403
