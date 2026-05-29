from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from app.core.paths import default_output_dir, get_config_dir


@dataclass(slots=True)
class AppSettings:
    default_output_directory: str
    markdown_flavor: str = "gfm"
    docx_engine_preference: str = "pandoc-first"
    pdf_extraction_mode: str = "plain-text"
    image_extraction_enabled: bool = False
    table_handling: str = "simple"
    pandoc_binary_path: str = ""
    libreoffice_binary_path: str = ""
    java_binary_path: str = ""
    tika_app_path: str = ""
    max_file_size_warning_mb: int = 100
    concurrency_limit: int = 1
    privacy_mode: bool = False

    @classmethod
    def default(cls) -> AppSettings:
        return cls(default_output_directory=str(default_output_dir()))


def settings_path(custom_path: Path | None = None) -> Path:
    if custom_path is not None:
        return custom_path
    return get_config_dir() / "settings.json"


def load_settings(custom_path: Path | None = None) -> AppSettings:
    target = settings_path(custom_path)
    if not target.exists():
        return AppSettings.default()

    raw = json.loads(target.read_text(encoding="utf-8"))
    known_fields = {field.name for field in fields(AppSettings)}
    filtered = {key: value for key, value in raw.items() if key in known_fields}
    return AppSettings(**filtered)


def save_settings(settings: AppSettings, custom_path: Path | None = None) -> Path:
    target = settings_path(custom_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
    return target
