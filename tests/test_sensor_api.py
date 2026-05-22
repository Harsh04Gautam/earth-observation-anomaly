from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_sensor_summary_endpoint_returns_location_and_latest_reading():
    response = client.get("/api/sensors")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1

    sensor = payload["sensors"][0]
    assert sensor["sensor_id"] == "99234"
    assert sensor["name"] == "sensor2837x"
    assert sensor["latitude"] == 45.4215
    assert sensor["longitude"] == -75.6972
    assert sensor["latest_temperature"] == -159.6692667
    assert sensor["latest_timestamp"] == "2026-05-12T00:50:00"
    assert sensor["anomaly_count"] == 6
