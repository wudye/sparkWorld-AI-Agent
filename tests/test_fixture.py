from .conftest import client

def test_get_user(client):
    response = client.get("/api/status")
    data = response.json()
    assert response.status_code == 200
    assert data["msg"] == "success"
