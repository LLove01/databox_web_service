from fastapi.testclient import TestClient
from backend.main import app  # Adjust the import path to match your project structure

client = TestClient(app)


def test_cors_headers():
    response = client.get(
        "/oauth-callback", headers={"Origin": "http://example.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_cors_preflight():
    response = client.options("/some-endpoint", headers={
        "Origin": "http://example.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-Custom-Header"
    })
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://example.com"
    assert "post" in response.headers["access-control-allow-methods"].lower()
    assert "x-custom-header" in response.headers["access-control-allow-headers"].lower()
