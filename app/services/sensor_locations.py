import json
from pathlib import Path

from app.models import SensorLocation


def load_sensor_locations(path: str | Path) -> dict[str, SensorLocation]:
    metadata_path = Path(path)
    if not metadata_path.exists():
        return {}

    raw_locations = json.loads(metadata_path.read_text(encoding="utf-8"))
    locations: dict[str, SensorLocation] = {}

    for item in raw_locations:
        location = SensorLocation(
            sensor_id=str(item["sensor_id"]),
            name=item["name"],
            latitude=float(item["latitude"]),
            longitude=float(item["longitude"]),
        )
        locations[location.sensor_id] = location

    return locations
