from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from app.core.paths import ensure_app_dirs

SELF_CHECK_REPORT_ENV = "OMNI_SELF_CHECK_REPORT"


@dataclass(slots=True)
class SelfCheckResult:
    ok: bool
    python_version: str
    app_dirs_ready: bool
    resources_ready: bool
    detail: str


def run_self_check() -> SelfCheckResult:
    app_dirs = ensure_app_dirs()
    resources_dir = Path(__file__).parent / "resources"
    resources_ready = (resources_dir / "styles" / "app.qss").exists()
    app_dirs_ready = all(path.exists() for path in app_dirs.values())
    ok = app_dirs_ready and resources_ready

    if ok:
        detail = "Self-check passed."
    elif not resources_ready:
        detail = "App resources are missing from the runtime package."
    else:
        detail = "One or more app directories could not be prepared."

    return SelfCheckResult(
        ok=ok,
        python_version=sys.version.split()[0],
        app_dirs_ready=app_dirs_ready,
        resources_ready=resources_ready,
        detail=detail,
    )


def write_self_check_report() -> int:
    report_path = os.environ.get(SELF_CHECK_REPORT_ENV)
    if report_path:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        result = run_self_check()
    except Exception as exc:
        result = SelfCheckResult(
            ok=False,
            python_version=sys.version.split()[0],
            app_dirs_ready=False,
            resources_ready=False,
            detail=f"Self-check failed: {exc}",
        )
    payload = json.dumps(asdict(result), indent=2)
    if report_path:
        Path(report_path).write_text(payload, encoding="utf-8")
    try:
        if sys.stdout is not None:
            print(payload)
    except OSError:
        pass
    return 0 if result.ok else 1
