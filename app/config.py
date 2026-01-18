import os
from pathlib import Path
from typing import Optional

APP_DATA_DIR_ENV = "APP_DATA_DIR"
APP_DEFAULT_LANG_ENV = "APP_DEFAULT_LANG"
APP_TEST_DATA_ENV = "APP_TEST_DATA"
APP_ALLOW_QUIT_ENV = "APP_ALLOW_QUIT"
SUPPORTED_LANGS = {"en", "fr"}


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


def get_default_language() -> str:
    lang = os.getenv(APP_DEFAULT_LANG_ENV, "en").strip().lower()
    return lang if lang in SUPPORTED_LANGS else "en"


def is_test_data_enabled() -> bool:
    value = os.getenv(APP_TEST_DATA_ENV, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def is_quit_allowed(client_host: Optional[str]) -> bool:
    if client_host in {"127.0.0.1", "::1"}:
        return True
    value = os.getenv(APP_ALLOW_QUIT_ENV, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}
