# Backend API Test Cases

This document outlines the complete set of backend test cases for the FastAPI AI Soil Health Assessment project, covering the Image Upload, Soil Analysis, Authentication APIs, and critical Edge Cases.

## Summary

This test plan includes **18 comprehensive test scenarios** designed to validate the stability, security, and accuracy of the backend services. The tests ensure that the API endpoints handle valid payloads correctly, reject malformed or malicious inputs securely, and degrade gracefully under network or server failure conditions.

---

## Test Cases

| Test Case ID | Scenario | Input | Expected Output | Actual Output | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **IMG-001** | Valid image upload | `file` = `soil_sample.jpg` (2MB, JPEG) | `201 Created` / `200 OK`<br>Returns JSON with `{ "id": 123, "filename": "..." }` | | |
| **IMG-002** | Invalid file format | `file` = `report.pdf` (PDF document) | `400 Bad Request` or `422 Unprocessable Entity`<br>Returns error: "Invalid file type" | | |
| **IMG-003** | Large file size limit | `file` = `high_res_soil.png` (12MB) | `413 Payload Too Large` or `400 Bad Request`<br>Returns error: "File exceeds 5MB limit" | | |
| **IMG-004** | Empty request (No file) | Empty `FormData` body | `422 Unprocessable Entity`<br>Returns error: "Field required" for `file` | | |
| **IMG-005** | Invalid form field name | `image_data` = `soil.jpg` (instead of `file`) | `422 Unprocessable Entity`<br>Returns error: "Field required" for `file` | | |
| **ANL-001** | Valid NPK + pH input (with image) | `N: 50, P: 40, K: 30, pH: 6.5, image_id: 123` | `200 OK`<br>Returns `{ "soil_health_score": 85, "health_band": "excellent", ... }` | | |
| **ANL-002** | Valid NPK + pH input (no image) | `N: 20, P: 10, K: 5, pH: 5.0, image_id: null` | `200 OK`<br>Returns valid analysis omitting image fusion data | | |
| **ANL-003** | Missing required values | `N: 50, P: 40` (missing K, pH) | `422 Unprocessable Entity`<br>Returns validation error for missing fields | | |
| **ANL-004** | Negative input values | `N: -10, P: 40, K: 30, pH: 6.5` | `422 Unprocessable Entity` or `400 Bad Request`<br>Returns error: "Nitrogen must be ≥ 0" | | |
| **ANL-005** | Invalid data type | `N: "fifty", P: 40, K: 30, pH: 6.5` | `422 Unprocessable Entity`<br>Returns validation error: "value is not a valid float" | | |
| **ANL-006** | Invalid image ID | `N: 50, P: 40, K: 30, pH: 6.5, image_id: 99999` | `404 Not Found`<br>Returns error: "Image with id=99999 not found" | | |
| **AUTH-001** | Valid user login | `email: user@test.com`, `password: StrongPass123` | `200 OK`<br>Returns `{ "access_token": "eyJ...", "token_type": "bearer" }` | | |
| **AUTH-002** | Invalid password | `email: user@test.com`, `password: WrongPass!` | `401 Unauthorized`<br>Returns error: "Incorrect email or password" | | |
| **AUTH-003** | Non-existing user login | `email: nobody@test.com`, `password: Password123` | `401 Unauthorized`<br>Returns error: "Incorrect email or password" | | |
| **AUTH-004** | SQL Injection attempt | `email: admin' OR '1'='1`, `password: pass` | `401 Unauthorized` or `422 Unprocessable Entity` (if email validated). Db secure. | | |
| **EDG-001** | Invalid API Endpoint | `POST /api/v1/analyze_soil` (Typo in URL) | `404 Not Found`<br>Returns standard FastAPI 404 response | | |
| **EDG-002** | Unauthorized access to protected route | `GET /auth/me` with missing/invalid JWT | `401 Unauthorized`<br>Returns error: "Not authenticated" | | |
| **EDG-003** | Backend not running (CORS/Network failure) | Send valid request while Uvicorn is stopped | `TypeError: Failed to fetch` (Frontend catch)<br>Connection Refused | | |

---

## Conclusion

This test suite covers the fundamental operations required for the Soil Health backend. The primary focus is on ensuring data integrity via Pydantic validation (`422 Unprocessable Entity`), secure authentication flows (`401 Unauthorized`), and proper resource handling (`404 Not Found` and `413 Payload Too Large`).

## Suggestions for Improvement

1. **Implement Rate Limiting:** Add `slowapi` to your FastAPI backend to prevent brute-force attacks on the `/auth/login` and `/api/v1/images` routes.
2. **Strict File Validation:** Relying on file extensions is insecure. Use `python-magic` to inspect the MIME type of uploaded files by reading the first few bytes (magic numbers) to guarantee it is actually an image, preventing disguised executables.
3. **Pydantic Bounds:** Ensure your `AnalyzeRequest` model in `analysis.py` has strict bounds using `Field(ge=0, le=14)` for pH and `Field(ge=0)` for N, P, K. Currently, it accepts any float, which requires manual bounds checking or risks returning illogical results.
