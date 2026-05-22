from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class SensorFileMetadata:
    source_file: str
    sensor_name: str
    date: date
    numeric_id: str
    measurement_type: str


@dataclass(frozen=True)
class SensorReading:
    sensor_id: str
    sensor_name: str
    date: date
    time: str
    timestamp: datetime
    temperature: float
    source_file: str
    source_path: Path


@dataclass(frozen=True)
class TemperatureAnomaly:
    sensor_id: str
    sensor_name: str
    date: date
    time: str
    timestamp: datetime
    temperature: float
    reason: str
    valid_range: tuple[float, float]
    source_file: str


@dataclass(frozen=True)
class SensorDataset:
    readings: list[SensorReading]
    anomalies: list[TemperatureAnomaly]
    missing_observations: list[datetime]
