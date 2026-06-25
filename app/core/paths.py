from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_cache_dir, user_config_dir, user_data_dir

APP_NAME = "OmniToMarkdown"
APP_AUTHOR = "OmniToMarkdown"
APP_HOME_ENV = "OMNI_TO_MARKDOWN_HOME"


def get_app_home_override() -> Path | None:
    app_home = os.environ.get(APP_HOME_ENV)
    if not app_home:
        return None
    return Path(app_home).expanduser()


def get_config_dir() -> Path:
    if app_home := get_app_home_override():
        return app_home / "config"
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))


def get_cache_dir() -> Path:
    if app_home := get_app_home_override():
        return app_home / "cache"
    return Path(user_cache_dir(APP_NAME, APP_AUTHOR))


def get_data_dir() -> Path:
    if app_home := get_app_home_override():
        return app_home / "data"
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def default_output_dir() -> Path:
    if app_home := get_app_home_override():
        return app_home / "output"
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
