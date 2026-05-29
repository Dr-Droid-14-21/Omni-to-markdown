from pathlib import Path

from app.core.settings import AppSettings, load_settings, save_settings


def test_load_settings_uses_defaults_when_file_missing(tmp_path: Path) -> None:
    settings_file = tmp_path / "settings.json"
    settings = load_settings(settings_file)

    assert isinstance(settings, AppSettings)
    assert settings.markdown_flavor == "gfm"


def test_save_then_load_round_trip(tmp_path: Path) -> None:
    settings_file = tmp_path / "settings.json"
    settings = AppSettings.default()
    settings.markdown_flavor = "commonmark"
    settings.privacy_mode = True

    save_settings(settings, settings_file)
    loaded = load_settings(settings_file)

    assert loaded.markdown_flavor == "commonmark"
    assert loaded.privacy_mode is True


def test_load_settings_ignores_unknown_future_fields(tmp_path: Path) -> None:
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        '{"default_output_directory": "out", "unknown_future_field": true}',
        encoding="utf-8",
    )

    loaded = load_settings(settings_file)

    assert loaded.default_output_directory == "out"
    assert loaded.tika_app_path == ""
