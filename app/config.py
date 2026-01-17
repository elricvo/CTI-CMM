import os
from pathlib import Path

APP_DATA_DIR_ENV = "APP_DATA_DIR"


def get_app_data_dir() -> Path:
    override = os.getenv(APP_DATA_DIR_ENV)
    if override:
        return Path(override).expanduser().resolve()
    return (Path(__file__).resolve().parents[1] / "data").resolve()


def get_db_path() -> Path:
    return get_app_data_dir() / "app.db"


def ensure_data_dir() -> Path:
    data_dir = get_app_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
