from __future__ import annotations

import json
import platform
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.core.models import ConversionResult


@dataclass(slots=True)
class RunReport:
    run_id: str
    generated_at_utc: str
    app_version: str
    os_name: str
    engine_versions: dict[str, str]
    total_files: int
    converted: int
    failed: int
    results: list[dict[str, object]]


def build_run_report(
    results: list[ConversionResult],
    app_version: str = "0.1.0",
    engine_versions: dict[str, str] | None = None,
) -> RunReport:
    converted = sum(1 for item in results if item.status.value == "converted")
    failed = sum(1 for item in results if item.status.value == "failed")
    run_id = uuid4().hex[:12]
    payload: list[dict[str, object]] = []

    for item in results:
        payload.append(
            {
                "source_path": str(item.source_path),
                "output_path": str(item.output_path) if item.output_path else "",
                "engine_name": item.engine_name,
                "status": item.status.value,
                "warning_count": len(item.warnings),
                "error_count": len(item.errors),
                "duration_ms": item.duration_ms,
                "warning_codes": [warning.code for warning in item.warnings],
                "error_codes": [error.code for error in item.errors],
            }
        )

    return RunReport(
        run_id=run_id,
        generated_at_utc=datetime.now(UTC).isoformat(),
        app_version=app_version,
        os_name=f"{platform.system()} {platform.release()}",
        engine_versions=engine_versions or {},
        total_files=len(results),
        converted=converted,
        failed=failed,
        results=payload,
    )


def write_run_reports(output_dir: Path, report: RunReport) -> tuple[Path, Path]:
    report_dir = output_dir / "reports" / report.run_id
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = report_dir / "conversion-report.json"
    markdown_path = report_dir / "conversion-report.md"

    json_path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    markdown_path.write_text(_render_markdown_report(report), encoding="utf-8")
    return json_path, markdown_path


def _render_markdown_report(report: RunReport) -> str:
    lines = [
        "# Conversion Report",
        "",
        f"- Run ID: `{report.run_id}`",
        f"- Generated (UTC): `{report.generated_at_utc}`",
        f"- App version: `{report.app_version}`",
        f"- OS: `{report.os_name}`",
        f"- Engine versions: `{_render_versions(report.engine_versions)}`",
        f"- Total files: `{report.total_files}`",
        f"- Converted: `{report.converted}`",
        f"- Failed: `{report.failed}`",
        "",
        "| Source file | Status | Engine | Warnings | Errors | Duration (ms) |",
        "|---|---|---|---:|---:|---:|",
    ]

    for item in report.results:
        source = Path(str(item["source_path"])).name
        lines.append(
            "| "
            f"{source} | {item['status']} | {item['engine_name']} | "
            f"{item['warning_count']} | {item['error_count']} | {item['duration_ms']} |"
        )

    lines.append("")
    return "\n".join(lines)


def _render_versions(engine_versions: dict[str, str]) -> str:
    if not engine_versions:
        return "not-collected"
    parts = [f"{name}={version}" for name, version in sorted(engine_versions.items())]
    return "; ".join(parts)
