from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "attendance.db"
DEFAULT_THRESHOLD = 75.0
