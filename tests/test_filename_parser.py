from datetime import date

import pytest

from app.services.filename_parser import parse_sensor_filename


def test_parse_assignment_sample_filename():
    metadata = parse_sensor_filename("sensor2837x_20260512-99234-TEMP.csv")

    assert metadata.sensor_name == "sensor2837x"
    assert metadata.date == date(2026, 5, 12)
    assert metadata.numeric_id == "99234"
    assert metadata.measurement_type == "TEMP"


def test_parse_hyphenated_example_filename():
    metadata = parse_sensor_filename("SENSOR_A-20231012-99234-TEMP.csv")

    assert metadata.sensor_name == "SENSOR_A"
    assert metadata.date == date(2023, 10, 12)
    assert metadata.numeric_id == "99234"
    assert metadata.measurement_type == "TEMP"


def test_reject_invalid_filename():
    with pytest.raises(ValueError):
        parse_sensor_filename("sensor.csv")
