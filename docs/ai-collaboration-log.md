# Task 3: AI Collaboration Log

## Summary

AI assistance was used as a coding partner to accelerate scaffolding, implementation planning, and documentation for the EO anomaly pipeline and pulse map. I kept the data contracts explicit, validated generated code with tests and live endpoint checks, and treated AI output as draft implementation rather than authoritative scientific logic.

## AI-Assisted Work

The following areas were generated or substantially drafted with AI assistance:

- FastAPI project structure, including `app/main.py`, Pydantic response schemas, and service modules.
- Filename parsing strategy for assignment-style CSV names such as `sensor2837x_20260512-99234-TEMP.csv`.
- CSV cleaning logic for repeated header rows, malformed rows, numeric temperature parsing, anomaly detection, and missing-minute detection.
- React/Vite dashboard structure, including API client functions, Leaflet map component, Chart.js trend component, sensor detail panel, and CSV upload panel.
- Documentation drafts for Task 1, Task 2, setup instructions, and this AI collaboration log.
- Test cases covering filename parsing, CSV parsing, anomaly detection, sensor summaries, and upload behavior.

AI was not used as the final source of truth for scientific decisions. The valid range came from the assignment prompt, and the lack of coordinates in the source CSV was handled explicitly rather than inferred from the readings.

## Where AI Needed Correction

Several AI-assisted drafts required human review and correction:

- **Filename assumptions:** The first plan could have treated the prefix separator as fixed, but the assignment examples use both `SENSOR_A-20231012-99234-TEMP.csv` and `sensor2837x_20260512-99234-TEMP.csv`. The parser was corrected to key off the stable suffix: `YYYYMMDD-NUMERIC_ID-MEASUREMENT.csv`.
- **Coordinates:** The assignment data does not contain latitude or longitude. Rather than fabricate hidden location data, the app now stores coordinates separately in `data/sensors.json` and requires coordinates during upload.
- **Missing observations:** Missing one-minute observations were kept separate from scientific anomalies. A missing row is a data-completeness issue, while the assignment defines anomalies as out-of-range readings.
- **Frontend/backend integration:** CORS and multipart upload support had to be added explicitly for the React dev server and upload form.
- **Test environment:** Pytest needed `pytest.ini` so imports resolve consistently from the repository root.
- **Generated docs drift:** After adding uploads and a second seeded sensor, documentation needed another pass so examples and test counts matched the actual app.

## Geospatial Prompting Approach

For the map requirement, I prompted the AI workflow to avoid assuming coordinates from the CSV because the sample only provides `time` and `temperature`. The geospatial requirement was handled as a separate metadata concern:

```text
Build the map from sensor metadata containing sensor_id, latitude, and longitude.
Do not infer coordinates from temperature readings.
If a CSV is uploaded, require the user to provide latitude and longitude.
Associate uploaded readings with the coordinate record using the numeric sensor ID parsed from the filename.
```

That led to the current design:

- `data/raw/*.csv` stores sensor reading files.
- `data/sensors.json` stores coordinate metadata keyed by `sensor_id`.
- `POST /api/uploads` accepts a CSV plus latitude and longitude.
- `GET /api/sensors` joins parsed readings with coordinate metadata for map display.
- Clicking a map marker fetches readings and anomalies for that marker's `sensor_id`.

## Validation Performed

AI-assisted code was validated with automated and manual checks:

```bash
source .venv/bin/activate
pytest -q

cd frontend
npm run build
```

Current validation result:

```text
9 backend tests passed
React production build completed successfully
```

Live endpoint checks were also performed during development for:

```text
GET /health
GET /api/sensors
GET /api/sensors/99234/readings
GET /api/anomalies
POST /api/uploads
```

## Human-in-the-Loop Decisions

The human review points were:

- Confirming that location metadata was absent from the original assignment data.
- Choosing to require coordinates during upload rather than inventing them.
- Keeping missing observations separate from anomaly records.
- Reviewing and correcting generated documentation after feature changes.
- Running tests and builds before each commit.

The final implementation treats AI as an accelerator for boilerplate, structure, and iteration, while data interpretation, geospatial assumptions, and validation remain explicit engineering decisions.
