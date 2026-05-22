from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str


class SensorFileResponse(BaseModel):
    source_file: str
    sensor_name: str
    date: date
    numeric_id: str
    measurement_type: str


class ReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sensor_id: str
    sensor_name: str
    date: date
    time: str
    timestamp: datetime
    temperature: float
    source_file: str


class AnomalyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sensor_id: str
    sensor_name: str
    date: date
    time: str
    timestamp: datetime
    temperature: float
    reason: str
    valid_range: tuple[float, float]
    source_file: str


class ValidRangeResponse(BaseModel):
    min: float
    max: float


class AnomalyListResponse(BaseModel):
    count: int
    valid_range: ValidRangeResponse
    anomalies: list[AnomalyResponse]


class ReadingListResponse(BaseModel):
    count: int
    readings: list[ReadingResponse]


class MissingObservationListResponse(BaseModel):
    count: int
    missing_observations: list[datetime]


class SensorSummaryResponse(BaseModel):
    sensor_id: str
    name: str
    latitude: float
    longitude: float
    latest_temperature: float | None
    latest_timestamp: datetime | None
    anomaly_count: int


class SensorSummaryListResponse(BaseModel):
    count: int
    sensors: list[SensorSummaryResponse]
