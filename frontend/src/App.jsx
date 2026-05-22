import { useCallback, useEffect, useMemo, useState } from 'react';
import { getHealth, getMissingObservations, getSensorAnomalies, getSensorReadings, getSensors } from './api/eoApi.js';
import SensorMap from './components/SensorMap.jsx';
import SensorDetails from './components/SensorDetails.jsx';
import StatusPanel from './components/StatusPanel.jsx';
import UploadPanel from './components/UploadPanel.jsx';

function App() {
  const [apiStatus, setApiStatus] = useState('checking');
  const [sensors, setSensors] = useState([]);
  const [selectedSensorId, setSelectedSensorId] = useState(null);
  const [readings, setReadings] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [missingObservations, setMissingObservations] = useState([]);
  const [error, setError] = useState('');

  const loadDashboard = useCallback(async (preferredSensorId = null) => {
    try {
      const [health, sensorPayload, missingPayload] = await Promise.all([
        getHealth(),
        getSensors(),
        getMissingObservations(),
      ]);

      setApiStatus(health.status);
      setSensors(sensorPayload.sensors);
      setMissingObservations(missingPayload.missing_observations);
      setSelectedSensorId((currentSensorId) => {
        if (preferredSensorId) {
          return preferredSensorId;
        }
        if (currentSensorId && sensorPayload.sensors.some((sensor) => sensor.sensor_id === currentSensorId)) {
          return currentSensorId;
        }
        return sensorPayload.sensors[0]?.sensor_id ?? null;
      });
      setError('');
    } catch (err) {
      setApiStatus('offline');
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    if (!selectedSensorId) {
      return;
    }

    async function loadSensorDetails() {
      try {
        const [readingPayload, anomalyPayload] = await Promise.all([
          getSensorReadings(selectedSensorId),
          getSensorAnomalies(selectedSensorId),
        ]);

        setReadings(readingPayload.readings);
        setAnomalies(anomalyPayload.anomalies);
      } catch (err) {
        setError(err.message);
      }
    }

    loadSensorDetails();
  }, [selectedSensorId]);

  const selectedSensor = useMemo(
    () => sensors.find((sensor) => sensor.sensor_id === selectedSensorId) ?? null,
    [selectedSensorId, sensors],
  );

  return (
    <main className="dashboard-shell">
      <header className="top-bar">
        <div>
          <h1>EO Pulse Map</h1>
          <p>Sensor anomaly monitoring</p>
        </div>
        <StatusPanel apiStatus={apiStatus} sensorCount={sensors.length} error={error} />
      </header>

      <section className="dashboard-grid">
        <SensorMap
          sensors={sensors}
          selectedSensorId={selectedSensorId}
          onSelectSensor={setSelectedSensorId}
        />
        <div className="side-rail">
          <UploadPanel onUploaded={(upload) => loadDashboard(upload.sensor_id)} />
          <SensorDetails
            sensor={selectedSensor}
            readings={readings}
            anomalies={anomalies}
            missingObservations={missingObservations}
          />
        </div>
      </section>
    </main>
  );
}

export default App;
