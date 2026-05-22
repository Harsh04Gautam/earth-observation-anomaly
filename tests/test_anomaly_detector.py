from app.services.csv_loader import load_sensor_file


def test_loader_finds_temperature_anomalies():
    dataset = load_sensor_file("data/raw/sensor2837x_20260512-99234-TEMP.csv")

    assert [anomaly.time for anomaly in dataset.anomalies] == [
        "00:10",
        "00:26",
        "00:47",
        "00:48",
        "00:49",
        "00:50",
    ]
    assert dataset.anomalies[0].reason == "below_minimum"
    assert dataset.anomalies[1].reason == "above_maximum"
