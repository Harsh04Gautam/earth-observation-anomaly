# Task 1: Data Processing & Automation

## Objective

Task 1 implements a small FastAPI service that processes messy Earth Observation sensor CSV files, identifies temperature anomalies, and exposes cleaned results through REST API endpoints.

The implemented valid temperature range is:

```text
-50.0 to 60.0
```

Any reading below `-50.0` is classified as `below_minimum`. Any reading above `60.0` is classified as `above_maximum`.

## Files Added

```text
app/
  main.py
  config.py
  models.py
  schemas.py
  services/
    filename_parser.py
    csv_loader.py
    anomaly_detector.py

data/
  raw/
    sensor2837x_20260512-99234-TEMP.csv

tests/
  test_filename_parser.py
  test_csv_loader.py
  test_anomaly_detector.py

requirements.txt
pytest.ini
README.md
```

## Filename Parsing

The parser supports both filename formats shown in the assignment:

```text
SENSOR_A-20231012-99234-TEMP.csv
sensor2837x_20260512-99234-TEMP.csv
```

The implemented parser extracts:

```json
{
  "sensor_name": "sensor2837x",
  "date": "2026-05-12",
  "numeric_id": "99234",
  "measurement_type": "TEMP"
}
```

The parser intentionally keys off the stable suffix:

```text
YYYYMMDD-NUMERIC_ID-MEASUREMENT.csv
```

This avoids brittle logic around the sensor prefix, since the prompt shows both underscore and hyphen separators before the date.

## CSV Cleaning

CSV processing is handled in `app/services/csv_loader.py`.

The loader:

- Reads CSV files from `data/raw`.
- Handles UTF-8 BOMs.
- Skips malformed rows.
- Skips repeated or messy header rows such as `Time, Temperature`.
- Accepts only rows where the first column is valid `HH:MM` time.
- Accepts only rows where the second column is a valid floating-point temperature.
- Combines the parsed file date with each row time to create an ISO timestamp.
- Sorts readings by timestamp.

Example cleaned reading:

```json
{
  "sensor_id": "99234",
  "sensor_name": "sensor2837x",
  "date": "2026-05-12",
  "time": "00:10",
  "timestamp": "2026-05-12T00:10:00",
  "temperature": -126.2359584,
  "source_file": "sensor2837x_20260512-99234-TEMP.csv"
}
```

## Missing Observations

The assignment states that sensors record one observation per minute, but some observations may be missing.

The implementation detects missing minute observations separately from anomalies. This is deliberate because the assignment defines anomalies as scientific out-of-range readings, not missing rows.

For the sample CSV, `00:31` is omitted, so the API reports:

```json
{
  "count": 1,
  "missing_observations": [
    "2026-05-12T00:31:00"
  ]
}
```

## Anomaly Detection

Anomaly detection is handled in `app/services/anomaly_detector.py`.

Each anomaly includes:

```json
{
  "sensor_id": "99234",
  "sensor_name": "sensor2837x",
  "date": "2026-05-12",
  "time": "00:10",
  "timestamp": "2026-05-12T00:10:00",
  "temperature": -126.2359584,
  "reason": "below_minimum",
  "valid_range": [-50.0, 60.0],
  "source_file": "sensor2837x_20260512-99234-TEMP.csv"
}
```

The sample dataset currently produces six anomalies:

```text
00:10  -126.2359584   below_minimum
00:26    70.69217748  above_maximum
00:47   -52.44321138  below_minimum
00:48   -54.38217334  below_minimum
00:49   -54.71100496  below_minimum
00:50  -159.6692667   below_minimum
```

## API Endpoints

The FastAPI app is defined in `app/main.py`.

Run the server:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

The API docs are available at:

```text
http://127.0.0.1:8000/docs
```

Available endpoints:

```text
GET /health
GET /api/files
GET /api/readings
GET /api/anomalies
GET /api/missing-observations
GET /api/sensors/{sensor_id}/readings
GET /api/sensors/{sensor_id}/anomalies
```

Primary Task 1 endpoint:

```text
GET /api/anomalies
```

Example response shape:

```json
{
  "count": 6,
  "valid_range": {
    "min": -50.0,
    "max": 60.0
  },
  "anomalies": []
}
```

## Tests

The tests cover:

- Assignment sample filename parsing.
- Hyphenated example filename parsing.
- Invalid filename rejection.
- Messy CSV header skipping.
- Valid row parsing.
- Missing observation detection.
- Temperature anomaly detection.

Run tests:

```bash
source .venv/bin/activate
pytest -q
```

Current result:

```text
6 passed
```

## Verification Performed

The implementation was verified with:

```bash
pytest -q
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/api/files
curl -s http://127.0.0.1:8000/api/readings
curl -s http://127.0.0.1:8000/api/anomalies
curl -s http://127.0.0.1:8000/api/missing-observations
curl -s http://127.0.0.1:8000/api/sensors/99234/anomalies
```

Observed results:

- `/health` returned `{"status":"ok"}`.
- `/api/files` returned the parsed sample CSV metadata.
- `/api/readings` returned `49` cleaned readings.
- `/api/anomalies` returned `6` anomalies.
- `/api/missing-observations` returned `1` missing observation.
- `/api/sensors/99234/anomalies` returned the six anomalies for sensor `99234`.

## Design Notes

The current implementation loads CSV data from disk on request. That is acceptable for Task 1 because the assignment sample is small and this keeps the data-processing behavior easy to inspect.

For a larger version, the ingestion layer should move parsed readings and anomaly records into a database such as PostgreSQL with TimescaleDB or PostGIS, depending on whether time-series performance or geospatial querying is the first bottleneck. The FastAPI endpoints could then query indexed tables instead of reparsing CSV files per request.
