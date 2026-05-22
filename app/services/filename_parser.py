import re
from datetime import datetime
from pathlib import Path

from app.models import SensorFileMetadata

FILENAME_PATTERN = re.compile(
    r"^(?P<sensor_name>.+?)[_-](?P<date>\d{8})-(?P<numeric_id>\d+)-(?P<measurement_type>[A-Za-z]+)\.csv$"
)


def parse_sensor_filename(path: str | Path) -> SensorFileMetadata:
    source_file = Path(path).name
    match = FILENAME_PATTERN.match(source_file)
    if not match:
        raise ValueError(
            "Sensor file names must end with YYYYMMDD-NUMERIC_ID-MEASUREMENT.csv"
        )

    parsed_date = datetime.strptime(match.group("date"), "%Y%m%d").date()
    return SensorFileMetadata(
        source_file=source_file,
        sensor_name=match.group("sensor_name"),
        date=parsed_date,
        numeric_id=match.group("numeric_id"),
        measurement_type=match.group("measurement_type").upper(),
    )
