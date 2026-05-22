# EO Anomaly Pipeline & Pulse Map

Implementation for the Earth Observation candidate assignment. The FastAPI backend reads messy sensor CSV files from `data/raw`, parses the file metadata, cleans valid time-series rows, detects temperature readings outside the scientific range `-50` to `60`, and exposes the result through REST endpoints. The React frontend renders a Leaflet pulse map, supports CSV uploads with coordinates, and shows a Chart.js reading trend for the selected sensor.

## Backend Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API docs at `http://127.0.0.1:8000/docs`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open the dashboard at `http://127.0.0.1:5173`.

## Useful Endpoints

```text
GET /health
GET /api/files
POST /api/uploads
GET /api/sensors
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

Frontend build:

```bash
cd frontend
npm run build
```

## Notes

The filename parser accepts both assignment examples: `SENSOR_A-20231012-99234-TEMP.csv` and `sensor2837x_20260512-99234-TEMP.csv`. CSV loading skips repeated or malformed header rows such as `Time, Temperature`, preserves source file metadata, and reports missing one-minute observations separately from scientific anomalies.

The source CSV does not include sensor coordinates, so `data/sensors.json` supplies latitude and longitude values for visualization. The upload form requires coordinates for each uploaded CSV and stores them in that metadata file. In a production pipeline those coordinates should come from authoritative sensor metadata rather than manual entry.
