const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

export function getHealth() {
  return request('/health');
}

export function getSensors() {
  return request('/api/sensors');
}

export function getSensorReadings(sensorId) {
  return request(`/api/sensors/${sensorId}/readings`);
}

export function getSensorAnomalies(sensorId) {
  return request(`/api/sensors/${sensorId}/anomalies`);
}

export function getMissingObservations() {
  return request('/api/missing-observations');
}
