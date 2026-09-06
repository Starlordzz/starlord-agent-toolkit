"""
API Route integration tests using FastAPI TestClient.
"""
from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "multi-uiautomator2-server"

def test_server_status():
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "watchdog" in data
    assert "connected_devices" in data

def test_config_idle_timeout():
    response = client.post("/config/idle-timeout", json={"idle_timeout": 120})
    assert response.status_code == 200
    data = response.json()
    assert data["idle_timeout"] == 120

    # Reset back to 60
    client.post("/config/idle-timeout", json={"idle_timeout": 60})

def test_device_list():
    response = client.get("/device/list")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "devices" in data

if __name__ == "__main__":
    test_health_check()
    test_server_status()
    test_config_idle_timeout()
    test_device_list()
    print("All route tests passed!")

