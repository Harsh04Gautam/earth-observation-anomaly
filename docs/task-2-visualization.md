# Task 2: Interactive Visualization

## Objective

Task 2 adds a React dashboard that consumes the FastAPI API, displays sensor locations on an interactive Leaflet map, color-codes sensor intensity, and renders a Chart.js time-series trend when a sensor is selected.

## Stack

```text
React + Vite
Leaflet + react-leaflet
Chart.js + react-chartjs-2
FastAPI backend
```

React was chosen for Task 2 because the dashboard has stateful interactions: API health, selected sensor, map markers, anomaly summaries, and chart data. Vite keeps the local setup small and fast.

## Backend Additions

Task 2 adds sensor metadata:

```text
data/sensors.json
```

The assignment CSV does not include coordinates, so this file provides demo coordinates for visualization:

```json
[
  {
    "sensor_id": "99234",
    "name": "sensor2837x",
    "latitude": 45.4215,
    "longitude": -75.6972
  }
]
```

The backend now exposes:

```text
GET /api/sensors
```

Example response shape:

```json
{
  "count": 1,
  "sensors": [
    {
      "sensor_id": "99234",
      "name": "sensor2837x",
      "latitude": 45.4215,
      "longitude": -75.6972,
      "latest_temperature": -159.6692667,
      "latest_timestamp": "2026-05-12T00:50:00",
      "anomaly_count": 6
    }
  ]
}
```

FastAPI CORS is enabled for local Vite development at:

```text
http://localhost:5173
http://127.0.0.1:5173
```

## Frontend Structure

```text
frontend/
  index.html
  package.json
  src/
    App.jsx
    main.jsx
    api/
      eoApi.js
    components/
      SensorMap.jsx
      SensorDetails.jsx
      ReadingChart.jsx
      StatusPanel.jsx
    styles.css
```

## Dashboard Behavior

The React app:

- Checks `/health` and displays API status.
- Fetches `/api/sensors` to populate map markers.
- Fetches `/api/missing-observations` to surface missing one-minute observations.
- Fetches `/api/sensors/{sensor_id}/readings` when a marker is selected.
- Fetches `/api/sensors/{sensor_id}/anomalies` for the selected sensor summary.
- Renders a Leaflet circle marker for each sensor.
- Renders a Chart.js line chart with valid-range threshold lines at `-50` and `60`.

Marker colors:

```text
temperature < -50   blue
-50 to 60           green
temperature > 60    red
unknown             gray
```

## Run Locally

Backend:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Verification

Backend tests:

```bash
source .venv/bin/activate
pytest -q
```

Current result:

```text
7 passed
```

Frontend build:

```bash
cd frontend
npm run build
```

The production build completes successfully. Vite reports a large chunk warning because Leaflet and Chart.js are bundled into the dashboard entry point; this is acceptable for this small take-home app and can be improved later with code splitting.
