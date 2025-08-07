import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.main import app
from src.auth.security import create_access_token

client = TestClient(app)

@pytest.fixture
def test_token():
    access_token = create_access_token(
        data={"sub": "testuser"},
        expires_delta=timedelta(minutes=30)
    )
    return access_token

def test_read_main(test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/sensor-data/current", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert "ph" in data
    assert "turbidity" in data

def test_unauthorized_access():
    response = client.get("/sensor-data/current")
    assert response.status_code == 401

def test_generate_report(test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.post("/reports/generate", headers=headers)
    assert response.status_code == 200
    assert "report" in response.json()

@pytest.mark.parametrize("hours", [24, 48, 168])
def test_historical_data(test_token, hours):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get(f"/sensor-data/history?hours={hours}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
