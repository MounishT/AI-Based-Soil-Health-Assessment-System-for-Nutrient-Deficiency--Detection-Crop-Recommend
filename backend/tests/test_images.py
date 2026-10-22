import io
from fastapi.testclient import TestClient

def test_image_upload_success(client: TestClient):
    # Valid 1x1 GIF
    file_content = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    file_like = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/images",
        files={"file": ("dummy.jpg", file_like, "image/jpeg")}
    )
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data
    assert "filename" in data

def test_image_upload_invalid_type(client: TestClient):
    file_content = b"fake pdf content"
    file_like = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/images",
        files={"file": ("dummy.pdf", file_like, "application/pdf")}
    )
    assert response.status_code == 400
    assert "File type '.pdf' is not allowed" in response.json()["detail"]

def test_image_upload_no_file(client: TestClient):
    response = client.post("/api/v1/images")
    assert response.status_code == 422
