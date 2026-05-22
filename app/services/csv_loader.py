import csv
from datetime import datetime, timedelta
from pathlib import Path

from app.config import MAX_TEMPERATURE, MIN_TEMPERATURE
from app.models import SensorDataset, SensorReading
from app.services.anomaly_detector import find_temperature_anomalies
from app.services.filename_parser import parse_sensor_filename


def load_sensor_file(path: str | Path) -> SensorDataset:
    source_path = Path(path)
    metadata = parse_sensor_filename(source_path)
    readings: list[SensorReading] = []

    with source_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            reading = _parse_reading_row(row, source_path, metadata)
            if reading is not None:
                readings.append(reading)

    readings.sort(key=lambda reading: reading.timestamp)
    anomalies = find_temperature_anomalies(
        readings,
        minimum=MIN_TEMPERATURE,
        maximum=MAX_TEMPERATURE,
    )

    return SensorDataset(
        readings=readings,
        anomalies=anomalies,
        missing_observations=find_missing_observations(readings),
    )


def load_sensor_directory(directory: str | Path) -> SensorDataset:
    all_readings: list[SensorReading] = []
    all_missing: list[datetime] = []

    for path in sorted(Path(directory).glob("*.csv")):
        dataset = load_sensor_file(path)
        all_readings.extend(dataset.readings)
        all_missing.extend(dataset.missing_observations)

    all_readings.sort(key=lambda reading: (reading.sensor_id, reading.timestamp))
    anomalies = find_temperature_anomalies(
        all_readings,
        minimum=MIN_TEMPERATURE,
        maximum=MAX_TEMPERATURE,
    )

    return SensorDataset(
        readings=all_readings,
        anomalies=anomalies,
        missing_observations=sorted(all_missing),
    )


def find_missing_observations(readings: list[SensorReading]) -> list[datetime]:
    if len(readings) < 2:
        return []

    timestamps = {reading.timestamp for reading in readings}
    current = min(timestamps)
    end = max(timestamps)
    missing: list[datetime] = []

    while current < end:
        current += timedelta(minutes=1)
        if current not in timestamps:
            missing.append(current)

    return missing


def _parse_reading_row(row, source_path: Path, metadata) -> SensorReading | None:
    if len(row) < 2:
        return None

    raw_time = row[0].strip()
    raw_temperature = row[1].strip()

    try:
        parsed_time = datetime.strptime(raw_time, "%H:%M").time()
        temperature = float(raw_temperature)
    except ValueError:
        return None

    timestamp = datetime.combine(metadata.date, parsed_time)
    return SensorReading(
        sensor_id=metadata.numeric_id,
        sensor_name=metadata.sensor_name,
        date=metadata.date,
        time=raw_time,
        timestamp=timestamp,
        temperature=temperature,
        source_file=metadata.source_file,
        source_path=source_path,
    )
