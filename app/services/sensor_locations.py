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


def upsert_sensor_location(path: str | Path, location: SensorLocation) -> None:
    metadata_path = Path(path)
    locations = load_sensor_locations(metadata_path)
    locations[location.sensor_id] = location

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = [
        {
            "sensor_id": item.sensor_id,
            "name": item.name,
            "latitude": item.latitude,
            "longitude": item.longitude,
        }
        for item in sorted(locations.values(), key=lambda item: item.sensor_id)
    ]
    metadata_path.write_text(
        json.dumps(serialized, indent=2) + "\n",
        encoding="utf-8",
    )
