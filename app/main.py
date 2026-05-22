from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    DATA_DIR,
    MAX_TEMPERATURE,
    MIN_TEMPERATURE,
    SENSOR_METADATA_PATH,
)
from app.schemas import (
    AnomalyListResponse,
    HealthResponse,
    MissingObservationListResponse,
    ReadingListResponse,
    SensorFileResponse,
    SensorSummaryListResponse,
    SensorSummaryResponse,
    ValidRangeResponse,
)
from app.services.csv_loader import load_sensor_directory
from app.services.filename_parser import parse_sensor_filename
from app.services.sensor_locations import load_sensor_locations

app = FastAPI(
    title="EO Anomaly Pipeline API",
    description="API for processing and visualizing Earth Observation sensor CSV files.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/api/sensors", response_model=SensorSummaryListResponse)
def list_sensors() -> SensorSummaryListResponse:
    dataset = load_sensor_directory(DATA_DIR)
    locations = load_sensor_locations(SENSOR_METADATA_PATH)
    sensor_ids = sorted({reading.sensor_id for reading in dataset.readings} | set(locations))
    sensors: list[SensorSummaryResponse] = []

    for sensor_id in sensor_ids:
        location = locations.get(sensor_id)
        readings = [
            reading for reading in dataset.readings if reading.sensor_id == sensor_id
        ]
        anomalies = [
            anomaly for anomaly in dataset.anomalies if anomaly.sensor_id == sensor_id
        ]
        latest = max(readings, key=lambda reading: reading.timestamp) if readings else None

        sensors.append(
            SensorSummaryResponse(
                sensor_id=sensor_id,
                name=location.name if location else latest.sensor_name if latest else sensor_id,
                latitude=location.latitude if location else 0.0,
                longitude=location.longitude if location else 0.0,
                latest_temperature=latest.temperature if latest else None,
                latest_timestamp=latest.timestamp if latest else None,
                anomaly_count=len(anomalies),
            )
        )

    return SensorSummaryListResponse(count=len(sensors), sensors=sensors)


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
