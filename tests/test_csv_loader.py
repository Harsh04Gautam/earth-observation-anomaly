from datetime import datetime

from app.services.csv_loader import load_sensor_file


def test_loader_skips_messy_headers_and_parses_readings():
    dataset = load_sensor_file("data/raw/sensor2837x_20260512-99234-TEMP.csv")

    assert dataset.readings[0].time == "00:01"
    assert dataset.readings[0].temperature == -39.5
    assert len(dataset.readings) == 49


def test_loader_detects_missing_minute_observations():
    dataset = load_sensor_file("data/raw/sensor2837x_20260512-99234-TEMP.csv")

    assert dataset.missing_observations == [datetime(2026, 5, 12, 0, 31)]
