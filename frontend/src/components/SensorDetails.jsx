import ReadingChart from './ReadingChart.jsx';

function formatTemperature(value) {
  return value == null ? 'No reading' : `${value.toFixed(2)} C`;
}

function SensorDetails({ sensor, readings, anomalies, missingObservations }) {
  if (!sensor) {
    return (
      <aside className="detail-panel">
        <p className="empty-state">No sensor selected.</p>
      </aside>
    );
  }

  return (
    <aside className="detail-panel">
      <div className="sensor-heading">
        <div>
          <h2>{sensor.name}</h2>
          <p>Sensor {sensor.sensor_id}</p>
        </div>
        <span className={sensor.anomaly_count > 0 ? 'status-badge alert' : 'status-badge'}>
          {sensor.anomaly_count} anomalies
        </span>
      </div>

      <div className="metric-grid">
        <div>
          <span>Latest reading</span>
          <strong>{formatTemperature(sensor.latest_temperature)}</strong>
        </div>
        <div>
          <span>Readings</span>
          <strong>{readings.length}</strong>
        </div>
        <div>
          <span>Missing observations</span>
          <strong>{missingObservations.length}</strong>
        </div>
        <div>
          <span>Location</span>
          <strong>{sensor.latitude.toFixed(4)}, {sensor.longitude.toFixed(4)}</strong>
        </div>
      </div>

      <ReadingChart readings={readings} anomalies={anomalies} />

      <div className="anomaly-list">
        <h3>Recent anomalies</h3>
        {anomalies.length === 0 ? (
          <p>No out-of-range readings.</p>
        ) : (
          <ul>
            {anomalies.slice(-6).map((anomaly) => (
              <li key={`${anomaly.sensor_id}-${anomaly.timestamp}`}>
                <span>{anomaly.time}</span>
                <strong>{anomaly.temperature.toFixed(2)} C</strong>
                <em>{anomaly.reason.replace('_', ' ')}</em>
              </li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}

export default SensorDetails;
