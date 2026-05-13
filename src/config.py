from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_PATH = DATA_DIR / "raw" / "food_delivery_analytics_cleaned.csv"
STAGING_DIR = DATA_DIR / "staging"
PROCESSED_DIR = DATA_DIR / "processed"
WAREHOUSE_DIR = DATA_DIR / "warehouse"
LOG_DIR = BASE_DIR / "logs"

DW_PATH = WAREHOUSE_DIR / "food_delivery_dw.sqlite"

SIZE_THRESHOLD_MB = 100
CHUNK_SIZE = 200_000

COLUMN_ALIASES = {
    "order_hour": ["order_hour", "hour", "order_time_hour"],
    "day_of_week": ["day_of_week", "order_day_of_week", "dow"],
    "month": ["month", "order_month", "order_month_num"],
}


def ensure_dirs():
    for path in [STAGING_DIR, PROCESSED_DIR, WAREHOUSE_DIR, LOG_DIR]:
        path.mkdir(parents=True, exist_ok=True)
