def test_analyze_valid_input(client):
    response = client.post("/analyze", json={
        "field_id": 1,
        "nitrogen": 50.0,
        "phosphorus": 40.0,
        "potassium": 30.0,
        "ph": 6.5
    })
    assert response.status_code == 200
    data = response.json()
    assert "soil_health_score" in data
    assert "health_band" in data
    assert "diagnosis" in data

def test_analyze_missing_values(client):
    response = client.post("/analyze", json={
        "field_id": 1,
        "nitrogen": 50.0
    })
    assert response.status_code == 422

def test_analyze_invalid_type(client):
    response = client.post("/analyze", json={
        "field_id": 1,
        "nitrogen": "high",
        "phosphorus": 40.0,
        "potassium": 30.0,
        "ph": 6.5
    })
    assert response.status_code == 422

def test_analyze_with_invalid_image(client):
    response = client.post("/analyze", json={
        "field_id": 1,
        "nitrogen": 50.0,
        "phosphorus": 40.0,
        "potassium": 30.0,
        "ph": 6.5,
        "image_id": 99999
    })
    assert response.status_code == 404
