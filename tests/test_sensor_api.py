from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_sensor_summary_endpoint_returns_location_and_latest_reading():
    response = client.get("/api/sensors")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2

    sensors = {sensor["sensor_id"]: sensor for sensor in payload["sensors"]}
    sensor = sensors["99234"]
    assert sensor["sensor_id"] == "99234"
    assert sensor["name"] == "sensor2837x"
    assert sensor["latitude"] == 45.4215
    assert sensor["longitude"] == -75.6972
    assert sensor["latest_temperature"] == -159.6692667
    assert sensor["latest_timestamp"] == "2026-05-12T00:50:00"
    assert sensor["anomaly_count"] == 6

    toronto_sensor = sensors["88421"]
    assert toronto_sensor["name"] == "sensorToronto"
    assert toronto_sensor["latitude"] == 43.6532
    assert toronto_sensor["longitude"] == -79.3832
    assert toronto_sensor["latest_temperature"] == 6.8
    assert toronto_sensor["latest_timestamp"] == "2026-05-13T00:20:00"
    assert toronto_sensor["anomaly_count"] == 2
