# Part 2: Technical Assessment Questions

## 1. AI Implementation & Agentic Workflows

### The Context Window Strategy

For a 50-page methodology document, I would not put the entire document into the prompt by default. I would first separate stable global context from task-specific context. The prompt should include the user question, the map or dataset being discussed, the expected answer format, key definitions, and any directly relevant excerpts needed to answer the question. The model should not have to infer which parts of a long methodology are relevant from a full-document dump every time.

I would use RAG when the document is long, reused across many questions, or contains sections that are only occasionally relevant. The retrieval layer should chunk the document by logical sections, preserve titles/page numbers, and retrieve passages using both semantic search and metadata filters such as methodology section, variable name, map layer, or dataset version. For high-stakes scientific answers, I would have the agent cite retrieved passages, expose uncertainty when retrieval is weak, and stop if the answer depends on missing context. The context window is best for immediate task instructions and the top retrieved evidence; RAG is best for scalable, traceable access to the full methodology.

### Prompt Engineering for Data

For transforming messy scientific metadata into internal JSON, I would make the prompt schema-first and validation-oriented. I would include the target JSON schema, field definitions, allowed units, date formats, null-handling rules, and two or three representative examples. I would also explicitly tell the model not to invent missing values and to return a structured validation error when required fields cannot be inferred.

Example prompt structure:

```text
You convert scientific metadata strings into JSON matching this schema.
Return only valid JSON. Do not include prose.
If a required value is missing or ambiguous, set it to null and add an item to validation_errors.

Schema:
{
  "sensor_id": "string|null",
  "measurement_type": "TEMP|SOIL_MOISTURE|NDVI|null",
  "observation_date": "YYYY-MM-DD|null",
  "units": "string|null",
  "latitude": "number|null",
  "longitude": "number|null",
  "validation_errors": ["string"]
}

Rules:
- Do not guess coordinates.
- Normalize dates to ISO-8601.
- Preserve original units if conversion is uncertain.
- Numeric IDs should remain strings to preserve leading zeros.

Input:
"SENSOR_A-20231012-99234-TEMP.csv; units C; station unknown"
```

In production, I would still validate the output with code after the LLM response. The LLM can assist with messy extraction, but schema validation, type checking, unit conversion, and persistence should be deterministic.

### AI as a Coworker

My human-in-the-loop philosophy is that an AI agent can act autonomously when the task is reversible, well-scoped, testable, and does not require scientific judgment beyond documented rules. Examples include generating boilerplate, drafting tests, parsing known file formats, proposing API shapes, or summarizing logs. Even then, the agent should leave an audit trail and run validation before presenting results.

The agent should stop and ask for verification when the decision is irreversible, ambiguous, domain-specific, or could affect scientific interpretation. It should ask before inventing coordinates, changing anomaly thresholds, interpolating missing observations, deleting data, rewriting provenance, or choosing between competing CRS assumptions. For scientific software, I want the AI to accelerate implementation, but the developer or scientist should own the data semantics, thresholds, units, coordinate assumptions, and final acceptance.

## 2. Geospatial & Scientific Visualization

### Handling Scale

For 100,000 active points, I would first avoid rendering all points as DOM markers. The first strategies I would evaluate are viewport filtering, clustering, vector tiles, and WebGL rendering. At low zoom levels, the API should return clusters or aggregate summaries rather than individual sensors. At higher zoom levels, it can return individual points inside the current bounding box. This keeps payloads and browser work proportional to what the user can actually see.

For implementation, I would compare Leaflet clustering for moderate loads against WebGL options such as Deck.gl, MapLibre GL, or a WebGL overlay. For 100,000 frequently updating points, WebGL or vector tiles are usually the stronger long-term choice. I would also cache map tiles or cluster responses by bounding box, zoom, measurement type, and time window. The frontend should debounce map movement, cancel stale requests, and avoid re-rendering unchanged layers.

### The Projection Trap

I would debug CRS mismatches by checking both the data contract and the actual coordinates. First, I would verify the backend output format: GeoJSON requires coordinates in `[longitude, latitude]`, while Leaflet marker APIs usually take `[latitude, longitude]`. A simple lat/lon swap can make data appear off-center. I would inspect a few known points manually and confirm whether values fall into plausible ranges, for example latitude between `-90` and `90` and longitude between `-180` and `180`.

Next, I would confirm the source CRS. Web maps commonly display in Web Mercator tiles but accept WGS84 latitude/longitude at the API layer. If the backend emits projected meters from EPSG:3857 or a local projection but the frontend treats them as degrees, the data will look stretched or displaced. I would check metadata, run a known coordinate through a CRS transform, and add tests around geometry serialization. The fix is to standardize the API boundary, usually WGS84/EPSG:4326 for GeoJSON and Leaflet inputs, and preserve the original CRS separately for provenance.

### Dynamic Charting

Missing time-series data should be represented as missing, not silently filled. For short time ranges, I would show gaps in the line chart where observations are absent and optionally annotate the missing intervals. For longer time ranges, I would aggregate into time buckets and include quality metadata such as sample count, missing count, min, max, and average per bucket. That lets the visualization stay readable without pretending the record is complete.

I would only interpolate when the scientist explicitly chooses an interpolation mode and the chart labels it clearly. Even then, I would keep the raw observed series available and visually distinguish estimated values from measured values. For Earth Observation data, the difference between "no event happened" and "no observation was recorded" is important, so the UI should preserve that distinction.

## 3. Architecture & Efficiency

### The Design System ROI

I would measure design system ROI by looking at whether it reduces delivery friction for engineers and improves consistency for users. Six months later, I would compare feature delivery metrics before and after adoption: time to build common screens, number of one-off UI components, design QA defects, accessibility regressions, and review cycles needed for visual polish. I would also track how often teams use shared components instead of creating local variants.

I would pair quantitative metrics with developer feedback. A design system is valuable if engineers can move faster without repeatedly solving button states, form validation, tables, filters, modals, and chart layouts from scratch. I would survey engineers on usability, inspect component adoption in repositories, and review whether the system reduced duplicated CSS and inconsistent interaction patterns. The goal is not just a prettier UI library; it is faster, more reliable product delivery.

### Python/Django Integration

For heavy geospatial processing in Python and a responsive React or Vue frontend, I would keep the processing path asynchronous. The web API should accept work requests, validate inputs, create a job record, and enqueue processing through Celery, RQ, or a streaming system depending on workload shape. Python workers can run GDAL, Rasterio, GeoPandas, xarray, or domain-specific processing without blocking API threads. The frontend polls job status or subscribes to updates, then fetches processed outputs when ready.

The handoff should happen through durable storage and explicit job state rather than direct in-memory coupling. Raw files go to object storage, metadata and job state go to PostgreSQL/PostGIS, large time-series outputs go to TimescaleDB or another analytical store, and map-ready products can be cached as tiles or derived layers. The frontend receives lightweight summaries, progress, and URLs or IDs for processed products. This keeps the UI responsive, makes long-running processing retryable, and gives developers a clear audit trail when a geospatial task fails.
