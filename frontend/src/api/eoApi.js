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

export async function uploadSensorCsv({ file, latitude, longitude, name }) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('latitude', latitude);
  formData.append('longitude', longitude);
  if (name) {
    formData.append('name', name);
  }

  const response = await fetch(`${API_BASE_URL}/api/uploads`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? `Upload failed: ${response.status}`);
  }

  return response.json();
}
