from fastapi.testclient import TestClient
from uuid import uuid4

def test_404_not_found_returns_json(client: TestClient):
    res = client.get("/api/v1/some-nonexistent-endpoint")
    assert res.status_code == 404
    data = res.json()
    assert "detail" in data
    assert data["detail"] == "Not Found"

def test_422_validation_error_format(client: TestClient, db_session):
    # Missing required body parameter (prompt)
    res = client.post(
        "/api/v1/missions/universal",
        json={"project_id": str(uuid4())}
    )
    assert res.status_code == 422
    data = res.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
    assert data["detail"][0]["loc"] == ["body", "prompt"]
    assert data["detail"][0]["msg"] == "Field required"

def test_405_method_not_allowed(client: TestClient):
    # Using POST on an endpoint that only allows GET
    res = client.post("/api/v1/auth/me")
    assert res.status_code == 405
    data = res.json()
    assert "detail" in data
    assert data["detail"] == "Method Not Allowed"
