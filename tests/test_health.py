from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_returns_html() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "actions-study" in response.text
    assert "/health" in response.text


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app_name": "actions-study",
        "version": "0.1.0",
        "environment": "local",
    }
