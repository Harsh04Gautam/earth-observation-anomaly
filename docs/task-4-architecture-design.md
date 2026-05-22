# Task 4: Architecture & Design for 100,000 Sensors

## Functional Requirements

- Ingest sensor CSV files and eventually support continuous sensor feeds.
- Parse source filenames to extract sensor ID, observation date, and measurement type.
- Validate and clean time-series readings without silently inventing scientific data.
- Detect anomalies outside configured scientific ranges such as `-50` to `60` Celsius.
- Store sensor metadata, coordinates, readings, anomaly records, ingestion status, and data-quality issues.
- Expose APIs for map summaries, sensor-specific readings, anomalies, uploads, and processing status.
- Render an interactive dashboard where scientists can inspect sensor locations, intensity, and time-series trends.
- Support uploaded files and batch ingestion without blocking the user interface.

## Non-Functional Requirements

- **Scale:** Handle at least 100,000 sensors and high-volume time-series readings without loading all data into API memory.
- **Low latency:** Keep map interactions fast by returning viewport-filtered, aggregated, or tiled data instead of all points.
- **Reliability:** Make ingestion retryable and idempotent so duplicate uploads or worker retries do not corrupt data.
- **Data integrity:** Preserve raw files, cleaned records, anomaly records, validation errors, and provenance.
- **Scientific accuracy:** Represent missing observations explicitly and avoid interpolation unless the UI labels it clearly.
- **Observability:** Track ingestion jobs, worker failures, API latency, queue depth, and anomaly volumes.
- **Extensibility:** Support additional measurement types and scientific thresholds without rewriting the pipeline.
- **Security:** Validate uploads, limit file sizes, authenticate write endpoints, and avoid trusting client-supplied sensor identity beyond the parsed filename and authorized metadata.

## Core Entities

```text
Sensor
  id
  display_name
  latitude
  longitude
  coordinate_reference_system
  created_at
  updated_at

SensorFile
  id
  sensor_id
  source_filename
  object_storage_uri
  observation_date
  measurement_type
  checksum
  upload_status
  created_at

IngestionJob
  id
  sensor_file_id
  status
  queued_at
  started_at
  completed_at
  error_message
  retry_count

Reading
  sensor_id
  timestamp
  measurement_type
  value
  source_file_id
  quality_flag

Anomaly
  sensor_id
  timestamp
  measurement_type
  value
  threshold_min
  threshold_max
  reason
  source_file_id

MissingObservation
  sensor_id
  expected_timestamp
  measurement_type
  source_file_id

ScientificThreshold
  measurement_type
  min_value
  max_value
  unit
  effective_from
  effective_to
```

## API Endpoints

```text
POST /api/uploads
  Upload a CSV plus coordinate metadata. Creates a SensorFile and queues ingestion.

GET /api/uploads/{job_id}
  Return ingestion status, validation errors, row counts, and anomaly counts.

GET /api/sensors
  Return sensor summaries for the current map viewport or query filter.

GET /api/sensors/{sensor_id}
  Return sensor metadata and latest status.

GET /api/sensors/{sensor_id}/readings
  Return downsampled readings for a sensor and time range.

GET /api/sensors/{sensor_id}/anomalies
  Return anomalies for a sensor and time range.

GET /api/map/sensors?bbox=&zoom=&measurement_type=
  Return viewport-filtered map points, clusters, or vector-tile metadata.

GET /api/map/anomalies?bbox=&zoom=&time_range=
  Return anomaly-focused map data for the visible area.

GET /api/thresholds
  Return configured scientific ranges by measurement type.
```

At 100,000 sensors, `/api/sensors` should not return every sensor by default. It should require either pagination, a bounding box, or a map-tile style query.

## High-Level System Design

```text
React Dashboard
  -> FastAPI API
    -> PostgreSQL/PostGIS for sensor metadata and geospatial queries
    -> TimescaleDB hypertables for time-series readings and anomalies
    -> Redis for cache, sessions, and Celery broker
    -> Object storage for raw uploaded CSV files
    -> Celery workers for parsing, cleaning, anomaly detection, and aggregation
```

The upload path should become asynchronous. FastAPI receives the file, validates the filename and request metadata, stores the raw CSV in object storage, writes a `SensorFile` row, and enqueues a Celery task. The API immediately returns a job ID. Celery workers parse the CSV in chunks, normalize rows, write readings in bulk, compute anomalies, record missing observations, and update ingestion status. This keeps the request/response path responsive and makes failures retryable.

For near-real-time ingestion, Celery is acceptable for file-based batch processing, but I would evaluate Kafka, Redpanda, or AWS Kinesis if readings become continuous event streams. A common mature design is hybrid: Celery handles uploaded/batch files, while a streaming pipeline handles live telemetry. Both paths write into the same normalized storage model and anomaly tables.

## Data Storage Deep Dive

PostgreSQL with PostGIS should own sensor metadata because it gives strong relational constraints and spatial indexing. The `Sensor` table should have a `geometry(Point, 4326)` column with a GiST index so viewport queries can filter by bounding box efficiently. Coordinates should be stored in WGS84/EPSG:4326 at the API boundary because Leaflet expects latitude/longitude in that CRS. If upstream data arrives in another CRS, the ingestion layer should transform it explicitly and preserve the source CRS.

Readings should move out of flat files and into a time-series optimized store. TimescaleDB is a strong fit because it keeps SQL semantics while partitioning readings into hypertables by time, and optionally by sensor ID or hash partition. Indexes should support the common access pattern: `(sensor_id, timestamp DESC)` for selected-sensor charts and `(measurement_type, timestamp)` for aggregate anomaly queries. Older raw readings can be compressed, retained at lower resolution, or rolled up into hourly/daily aggregates while keeping anomaly records and raw files for auditability.

Raw CSV files should be immutable in object storage such as S3, GCS, or Azure Blob Storage. Store a checksum in `SensorFile` and make ingestion idempotent by using `(sensor_id, source_file_id, timestamp, measurement_type)` as a uniqueness boundary. If a worker retries, it should either upsert deterministically or detect that the file was already processed.

## Queue and Processing Deep Dive

Celery with Redis or RabbitMQ is a practical next step for this application because the current workload is file-based and CPU/IO-bound. The queue lets the API return quickly while parsing happens in workers. Workers should process CSVs in streaming chunks instead of loading whole files into memory. Bulk inserts should batch rows, for example 5,000 to 20,000 readings at a time, depending on database performance.

The ingestion job should have explicit states:

```text
queued -> parsing -> validating -> writing -> completed
queued -> parsing -> failed
```

Each job should record row counts, skipped rows, anomaly counts, missing-observation counts, and error messages. Scientists and developers need this metadata to distinguish sensor behavior from pipeline failure. A dead-letter queue or failed-job table should preserve unrecoverable failures for inspection.

Thresholds should be data-driven rather than hard-coded. A `ScientificThreshold` table lets the system support temperature today and other EO measurements later. Workers should load the active threshold for each measurement type and record the exact threshold values onto each anomaly so later threshold changes do not rewrite historical interpretation.

## Frontend Performance Deep Dive

The React dashboard should not render 100,000 standard Leaflet DOM markers. For the first scale step, I would evaluate viewport filtering and clustering: request only sensors inside the current bounding box and cluster at lower zoom levels. Leaflet marker clustering is useful for moderate scale, but for 100,000 active points WebGL rendering is usually the better default. Deck.gl, MapLibre GL, or a WebGL Leaflet overlay can draw large point layers without creating thousands of DOM nodes.

For very large maps, the backend should expose vector tiles or tile-like endpoints keyed by `z/x/y`, time range, and measurement type. Tiles can be cached at the CDN or API layer, and the client only asks for visible tiles. At low zoom, tiles should contain clusters or aggregates. At high zoom, they can contain individual sensors. This keeps payloads small and map interactions responsive.

Time-series charts need downsampling. When a scientist selects a sensor with years of minute-level readings, the API should return data appropriate for the chart width rather than millions of points. The backend can use bucketed aggregation such as min/max/avg per pixel bucket or per time interval. For scientific integrity, missing intervals should be returned as gaps or quality flags, not interpolated silently.

## API and Caching Deep Dive

Read-heavy endpoints should use cache keys that include viewport, zoom, measurement type, and time range. Redis can cache sensor summaries, cluster results, latest readings, and anomaly counts. Cache invalidation can be event-driven from ingestion completion: when a job finishes, invalidate affected sensor and tile keys.

The API should support pagination, bounding boxes, and explicit time ranges. Unbounded requests should be rejected or capped. This protects both the database and browser from accidental full-dataset scans.

## Observability and Operations

For production, I would add:

- Structured logs with `job_id`, `sensor_id`, and `source_file_id`.
- Metrics for queue depth, job duration, rows processed per second, skipped-row count, anomaly count, and API latency.
- Tracing across upload request, queue enqueue, worker processing, and database writes.
- Alerts for stuck jobs, high failure rates, stale latest readings, and database write latency.
- Admin views for failed uploads and validation errors.

These checks matter because scientific users need to know whether a quiet map means no anomalies, missing data, or a broken ingestion path.

## Two-Paragraph README Summary

To scale this architecture to 100,000 sensors, I would move the current file-on-request parsing into an asynchronous ingestion pipeline. FastAPI would validate uploads, store raw CSVs in object storage, create an ingestion job, and enqueue processing through Celery backed by Redis or RabbitMQ. Celery workers would parse files in chunks, write readings in bulk, detect anomalies using threshold records, and persist missing-observation quality flags. Sensor metadata and coordinates would live in PostgreSQL/PostGIS with spatial indexes, while readings and anomalies would live in TimescaleDB hypertables partitioned by time and sensor. Raw files would remain immutable for auditability, and each processed row would retain source-file provenance.

For frontend performance, the React map should not request or render all sensors at once. The API should return only viewport-filtered data, clustered summaries, or vector tiles based on zoom level and bounding box. At moderate scale Leaflet clustering is acceptable, but for 100,000 active points I would evaluate WebGL layers with Deck.gl or MapLibre GL. Charts should request downsampled readings for the selected time range, with missing observations represented as gaps or quality flags rather than silently interpolated. Redis/CDN caching for map tiles, latest sensor summaries, and anomaly counts would keep repeated dashboard interactions fast while ingestion jobs update affected cache keys when new data lands.
