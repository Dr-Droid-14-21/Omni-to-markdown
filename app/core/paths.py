from __future__ import annotations

from pathlib import Path

from platformdirs import user_cache_dir, user_config_dir, user_data_dir

APP_NAME = "OmniToMarkdown"
APP_AUTHOR = "OmniToMarkdown"


def get_config_dir() -> Path:
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))


def get_cache_dir() -> Path:
    return Path(user_cache_dir(APP_NAME, APP_AUTHOR))


def get_data_dir() -> Path:
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def default_output_dir() -> Path:
    return Path.home() / "Documents" / APP_NAME / "output"


def ensure_app_dirs() -> dict[str, Path]:
    dirs = {
        "config": get_config_dir(),
        "cache": get_cache_dir(),
        "data": get_data_dir(),
        "output": default_output_dir(),
    }
    for folder in dirs.values():
        folder.mkdir(parents=True, exist_ok=True)
    return dirs
