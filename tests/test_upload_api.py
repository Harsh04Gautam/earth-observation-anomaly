import json

from fastapi.testclient import TestClient

import app.main as main


client = TestClient(main.app)


def test_upload_sensor_csv_saves_file_and_location(monkeypatch, tmp_path):
    data_dir = tmp_path / "raw"
    metadata_path = tmp_path / "sensors.json"
    monkeypatch.setattr(main, "DATA_DIR", data_dir)
    monkeypatch.setattr(main, "SENSOR_METADATA_PATH", metadata_path)

    response = client.post(
        "/api/uploads",
        data={
            "latitude": "40.7128",
            "longitude": "-74.0060",
            "name": "Harbor Sensor",
        },
        files={
            "file": (
                "harbor_20260513-12345-TEMP.csv",
                b"time,temperature\n00:01,20\n00:02,88\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["sensor_id"] == "12345"
    assert payload["reading_count"] == 2
    assert payload["anomaly_count"] == 1
    assert (data_dir / "harbor_20260513-12345-TEMP.csv").exists()

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata == [
        {
            "sensor_id": "12345",
            "name": "Harbor Sensor",
            "latitude": 40.7128,
            "longitude": -74.006,
        }
    ]

    sensors_response = client.get("/api/sensors")
    assert sensors_response.status_code == 200
    sensors = sensors_response.json()["sensors"]
    assert sensors[0]["sensor_id"] == "12345"
    assert sensors[0]["latest_temperature"] == 88.0


def test_upload_rejects_missing_coordinates():
    response = client.post(
        "/api/uploads",
        data={"latitude": "100", "longitude": "0"},
        files={
            "file": (
                "bad_20260513-12345-TEMP.csv",
                b"time,temperature\n00:01,20\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Latitude must be between -90 and 90"
