from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

TRAY_KIND = "omni-stitch-tray"
TRAY_VERSION = 1


class StitchTrayError(ValueError):
    """Raised when a tray file is invalid or unreadable."""


@dataclass(slots=True)
class StitchTray:
    input_files: list[Path]
    output_path: Path | None = None


def save_stitch_tray(
    tray_path: Path,
    *,
    input_files: list[Path],
    output_path: Path | None = None,
) -> Path:
    if not input_files:
        msg = "stitch tray must contain at least one input file"
        raise StitchTrayError(msg)

    payload: dict[str, object] = {
        "kind": TRAY_KIND,
        "version": TRAY_VERSION,
        "saved_at_utc": datetime.now(UTC).isoformat(),
        "items": [{"path": str(path)} for path in input_files],
    }
    if output_path is not None:
        payload["output_path"] = str(output_path)

    tray_path.parent.mkdir(parents=True, exist_ok=True)
    tray_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return tray_path


def load_stitch_tray(tray_path: Path) -> StitchTray:
    try:
        raw = json.loads(tray_path.read_text(encoding="utf-8"))
    except OSError as exc:
        msg = f"unable to read tray file: {tray_path}"
        raise StitchTrayError(msg) from exc
    except json.JSONDecodeError as exc:
        msg = f"invalid tray json: {tray_path}"
        raise StitchTrayError(msg) from exc

    kind = str(raw.get("kind", ""))
    if kind != TRAY_KIND:
        msg = f"unsupported tray kind: {kind or 'missing'}"
        raise StitchTrayError(msg)

    version = int(raw.get("version", -1))
    if version != TRAY_VERSION:
        msg = f"unsupported tray version: {version}"
        raise StitchTrayError(msg)

    items = raw.get("items")
    if not isinstance(items, list) or not items:
        msg = "tray file has no items"
        raise StitchTrayError(msg)

    input_files: list[Path] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            msg = f"tray item at index {index} is invalid"
            raise StitchTrayError(msg)
        path_value = str(item.get("path", "")).strip()
        if not path_value:
            msg = f"tray item at index {index} is missing path"
            raise StitchTrayError(msg)
        input_files.append(Path(path_value))

    output_value = str(raw.get("output_path", "")).strip()
    output_path = Path(output_value) if output_value else None
    return StitchTray(input_files=input_files, output_path=output_path)
