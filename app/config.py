from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"

MIN_TEMPERATURE = -50.0
MAX_TEMPERATURE = 60.0
