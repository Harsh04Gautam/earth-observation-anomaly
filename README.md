# EO Anomaly Pipeline API

Task 1 implementation for the Earth Observation candidate assignment. The API reads messy sensor CSV files from `data/raw`, parses the file metadata, cleans valid time-series rows, detects temperature readings outside the scientific range `-50` to `60`, and exposes the result through FastAPI.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API docs at `http://127.0.0.1:8000/docs`.

## Useful Endpoints

```text
GET /health
GET /api/files
GET /api/readings
GET /api/anomalies
GET /api/missing-observations
GET /api/sensors/{sensor_id}/readings
GET /api/sensors/{sensor_id}/anomalies
```

## Tests

```bash
pytest
```

## Notes

The filename parser accepts both assignment examples: `SENSOR_A-20231012-99234-TEMP.csv` and `sensor2837x_20260512-99234-TEMP.csv`. CSV loading skips repeated or malformed header rows such as `Time, Temperature`, preserves source file metadata, and reports missing one-minute observations separately from scientific anomalies.
