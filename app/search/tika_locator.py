from __future__ import annotations

import sys
from pathlib import Path

TIKA_APP_VERSION = "3.2.3"
TIKA_APP_FILENAME = f"tika-app-{TIKA_APP_VERSION}.jar"


def bundled_tika_candidates() -> list[Path]:
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [repo_root / "tools" / "tika" / TIKA_APP_FILENAME]

    if getattr(sys, "frozen", False):
        executable_dir = Path(sys.executable).resolve().parent
        candidates.extend(
            [
                executable_dir / "tools" / "tika" / TIKA_APP_FILENAME,
                executable_dir / "_internal" / "tools" / "tika" / TIKA_APP_FILENAME,
            ]
        )
        bundle_dir = getattr(sys, "_MEIPASS", "")
        if bundle_dir:
            candidates.append(Path(bundle_dir) / "tools" / "tika" / TIKA_APP_FILENAME)

    return candidates


def resolve_tika_app_path(override: str = "") -> tuple[Path | None, str]:
    configured = override.strip()
    if configured:
        path = Path(configured).expanduser()
        if path.exists() and path.is_file():
            return path, ""
        return None, f"Configured Tika jar not found: {path}"

    for candidate in bundled_tika_candidates():
        if candidate.exists() and candidate.is_file():
            return candidate, ""

    locations = "; ".join(str(path) for path in bundled_tika_candidates())
    return None, f"Tika app jar was not found. Expected one of: {locations}"
