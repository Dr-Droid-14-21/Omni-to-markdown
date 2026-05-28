from pathlib import Path

from app.conversion.reports import build_run_report, write_run_reports
from app.core.models import ConversionResult, FileStatus


def _result(path_name: str, status: FileStatus) -> ConversionResult:
    source = Path(path_name)
    output = Path(f"{source.stem}.md")
    return ConversionResult(
        source_path=source,
        output_path=output,
        engine_name="pandoc",
        status=status,
        duration_ms=12,
    )


def test_build_run_report_counts_statuses() -> None:
    results = [
        _result("a.docx", FileStatus.CONVERTED),
        _result("b.odt", FileStatus.FAILED),
    ]
    report = build_run_report(results, app_version="0.1.0")

    assert report.total_files == 2
    assert report.converted == 1
    assert report.failed == 1
    assert report.app_version == "0.1.0"


def test_write_reports_creates_json_and_markdown(tmp_path: Path) -> None:
    results = [_result("a.docx", FileStatus.CONVERTED)]
    report = build_run_report(results, engine_versions={"pandoc": "pandoc 3.0.0"})

    json_path, markdown_path = write_run_reports(tmp_path, report)

    assert json_path.exists()
    assert markdown_path.exists()
    content = markdown_path.read_text(encoding="utf-8")
    assert "Conversion Report" in content
    assert "pandoc=pandoc 3.0.0" in content
