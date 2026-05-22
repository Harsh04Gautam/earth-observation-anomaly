import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';

const DEFAULT_CENTER = [45.4215, -75.6972];

function markerColor(temperature) {
  if (temperature == null) {
    return '#6b7280';
  }
  if (temperature < -50) {
    return '#2563eb';
  }
  if (temperature > 60) {
    return '#dc2626';
  }
  return '#15803d';
}

function markerRadius(sensor, selectedSensorId) {
  const baseRadius = Math.max(10, Math.min(24, Math.abs(sensor.latest_temperature ?? 0) / 7));
  return sensor.sensor_id === selectedSensorId ? baseRadius + 5 : baseRadius;
}

function SensorMap({ sensors, selectedSensorId, onSelectSensor }) {
  const center = sensors[0] ? [sensors[0].latitude, sensors[0].longitude] : DEFAULT_CENTER;

  return (
    <section className="map-panel" aria-label="Sensor map">
      <MapContainer center={center} zoom={8} scrollWheelZoom className="sensor-map">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {sensors.map((sensor) => {
          const color = markerColor(sensor.latest_temperature);
          return (
            <CircleMarker
              key={sensor.sensor_id}
              center={[sensor.latitude, sensor.longitude]}
              pathOptions={{
                color,
                fillColor: color,
                fillOpacity: 0.72,
                weight: sensor.sensor_id === selectedSensorId ? 4 : 2,
              }}
              radius={markerRadius(sensor, selectedSensorId)}
              eventHandlers={{
                click: () => onSelectSensor(sensor.sensor_id),
              }}
            >
              <Popup>
                <div className="map-popup">
                  <strong>{sensor.name}</strong>
                  <span>{sensor.sensor_id}</span>
                  <span>{sensor.latest_temperature?.toFixed(2)} C</span>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </section>
  );
}

export default SensorMap;
