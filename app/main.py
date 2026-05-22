from fastapi import FastAPI, HTTPException

from app.config import DATA_DIR, MAX_TEMPERATURE, MIN_TEMPERATURE
from app.schemas import (
    AnomalyListResponse,
    HealthResponse,
    MissingObservationListResponse,
    ReadingListResponse,
    SensorFileResponse,
    ValidRangeResponse,
)
from app.services.csv_loader import load_sensor_directory
from app.services.filename_parser import parse_sensor_filename

app = FastAPI(
    title="EO Anomaly Pipeline API",
    description="Task 1 API for processing Earth Observation sensor CSV files.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/api/files", response_model=list[SensorFileResponse])
def list_files() -> list[SensorFileResponse]:
    return [
        SensorFileResponse.model_validate(parse_sensor_filename(path).__dict__)
        for path in sorted(DATA_DIR.glob("*.csv"))
    ]


@app.get("/api/readings", response_model=ReadingListResponse)
def list_readings() -> ReadingListResponse:
    dataset = load_sensor_directory(DATA_DIR)
    return ReadingListResponse(count=len(dataset.readings), readings=dataset.readings)


@app.get("/api/anomalies", response_model=AnomalyListResponse)
def list_anomalies() -> AnomalyListResponse:
    dataset = load_sensor_directory(DATA_DIR)
    return AnomalyListResponse(
        count=len(dataset.anomalies),
        valid_range=ValidRangeResponse(min=MIN_TEMPERATURE, max=MAX_TEMPERATURE),
        anomalies=dataset.anomalies,
    )


@app.get("/api/missing-observations", response_model=MissingObservationListResponse)
def list_missing_observations() -> MissingObservationListResponse:
    dataset = load_sensor_directory(DATA_DIR)
    return MissingObservationListResponse(
        count=len(dataset.missing_observations),
        missing_observations=dataset.missing_observations,
    )


@app.get("/api/sensors/{sensor_id}/readings", response_model=ReadingListResponse)
def list_sensor_readings(sensor_id: str) -> ReadingListResponse:
    dataset = load_sensor_directory(DATA_DIR)
    readings = [reading for reading in dataset.readings if reading.sensor_id == sensor_id]
    if not readings:
        raise HTTPException(status_code=404, detail="Sensor not found")

    return ReadingListResponse(count=len(readings), readings=readings)


@app.get("/api/sensors/{sensor_id}/anomalies", response_model=AnomalyListResponse)
def list_sensor_anomalies(sensor_id: str) -> AnomalyListResponse:
    dataset = load_sensor_directory(DATA_DIR)
    sensor_exists = any(reading.sensor_id == sensor_id for reading in dataset.readings)
    if not sensor_exists:
        raise HTTPException(status_code=404, detail="Sensor not found")

    anomalies = [
        anomaly for anomaly in dataset.anomalies if anomaly.sensor_id == sensor_id
    ]
    return AnomalyListResponse(
        count=len(anomalies),
        valid_range=ValidRangeResponse(min=MIN_TEMPERATURE, max=MAX_TEMPERATURE),
        anomalies=anomalies,
    )
