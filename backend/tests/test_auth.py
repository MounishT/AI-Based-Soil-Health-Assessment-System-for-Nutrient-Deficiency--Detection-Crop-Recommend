def test_register_success(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "strongpassword123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"

def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "User One"
    })
    
    response = client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password456",
        "full_name": "User Two"
    })
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

def test_login_success(client):
    client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "password123",
        "full_name": "Login User"
    })
    
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password(client):
    client.post("/auth/register", json={
        "email": "login2@example.com",
        "password": "password123"
    })
    
    response = client.post("/auth/login", json={
        "email": "login2@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_non_existent_user(client):
    response = client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "password"
    })
    assert response.status_code == 401
