from pathlib import Path

from app.core import paths


def test_app_home_override_controls_runtime_directories(monkeypatch):
    app_home = Path("portable-profile")
    monkeypatch.setenv(paths.APP_HOME_ENV, str(app_home))

    assert paths.get_config_dir() == app_home / "config"
    assert paths.get_cache_dir() == app_home / "cache"
    assert paths.get_data_dir() == app_home / "data"
    assert paths.default_output_dir() == app_home / "output"
