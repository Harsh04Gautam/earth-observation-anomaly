from app.models import SensorReading, TemperatureAnomaly


def find_temperature_anomalies(
    readings: list[SensorReading],
    minimum: float,
    maximum: float,
) -> list[TemperatureAnomaly]:
    anomalies: list[TemperatureAnomaly] = []

    for reading in readings:
        if reading.temperature < minimum:
            reason = "below_minimum"
        elif reading.temperature > maximum:
            reason = "above_maximum"
        else:
            continue

        anomalies.append(
            TemperatureAnomaly(
                sensor_id=reading.sensor_id,
                sensor_name=reading.sensor_name,
                date=reading.date,
                time=reading.time,
                timestamp=reading.timestamp,
                temperature=reading.temperature,
                reason=reason,
                valid_range=(minimum, maximum),
                source_file=reading.source_file,
            )
        )

    return anomalies
