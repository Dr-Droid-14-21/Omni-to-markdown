from pathlib import Path

from app.conversion.dependency_check import DependencyStatus
from app.conversion.libreoffice_engine import LibreOfficeEngine
from app.core.models import ConversionPlan, FileStatus
from app.core.process import ProcessRunResult
from app.core.settings import AppSettings


def _settings() -> AppSettings:
    cfg = AppSettings.default()
    cfg.libreoffice_binary_path = ""
    return cfg


def _plan(source: Path, output: Path) -> ConversionPlan:
    return ConversionPlan(
        source_path=source,
        output_path=output,
        detected_extension=source.suffix.lower(),
        preferred_engine="libreoffice",
    )


def test_is_available_when_libreoffice_found(monkeypatch: object) -> None:
    def fake_detect(_: AppSettings) -> DependencyStatus:
        return DependencyStatus(name="libreoffice", available=True, path=r"C:\soffice.exe")

    monkeypatch.setattr("app.conversion.libreoffice_engine.detect_libreoffice", fake_detect)
    engine = LibreOfficeEngine(settings=_settings())

    assert engine.is_available().available is True


def test_convert_fails_for_unsupported_extension(tmp_path: Path) -> None:
    source = tmp_path / "scan.pdf"
    source.write_bytes(b"%PDF-1.7")
    output = tmp_path / "scan.md"

    engine = LibreOfficeEngine(settings=_settings())
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.FAILED
    assert result.errors[0].code == "UNSUPPORTED_EXTENSION"


def test_convert_handles_timeout(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "legacy.doc"
    source.write_text("legacy", encoding="utf-8")
    output = tmp_path / "legacy.md"

    def fake_detect(_: AppSettings) -> DependencyStatus:
        return DependencyStatus(name="libreoffice", available=True, path="soffice")

    def fake_run_process(_command: list[str], timeout_seconds: int) -> ProcessRunResult:
        assert timeout_seconds == 1
        return ProcessRunResult(
            returncode=-1,
            stdout="",
            stderr="",
            timed_out=True,
        )

    monkeypatch.setattr("app.conversion.libreoffice_engine.detect_libreoffice", fake_detect)
    monkeypatch.setattr("app.conversion.libreoffice_engine.run_process", fake_run_process)

    engine = LibreOfficeEngine(settings=_settings(), timeout_seconds=1)
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.FAILED
    assert result.errors[0].code == "LIBREOFFICE_TIMEOUT"


def test_convert_success_writes_normalized_output(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "legacy.doc"
    source.write_text("legacy", encoding="utf-8")
    output = tmp_path / "legacy.md"

    def fake_detect(_: AppSettings) -> DependencyStatus:
        return DependencyStatus(name="libreoffice", available=True, path="soffice")

    def fake_run_process(command: list[str], timeout_seconds: int) -> ProcessRunResult:
        assert timeout_seconds == 180
        out_dir = Path(command[command.index("--outdir") + 1])
        out_dir.mkdir(parents=True, exist_ok=True)
        target = command[command.index("--convert-to") + 1]
        if target == "docx":
            (out_dir / f"{source.stem}.docx").write_bytes(b"PK")
        elif target == "html":
            (out_dir / f"{source.stem}.html").write_text("<p>Line</p>", encoding="utf-8")
        return ProcessRunResult(returncode=0, stdout="", stderr="", timed_out=False)

    monkeypatch.setattr("app.conversion.libreoffice_engine.detect_libreoffice", fake_detect)
    monkeypatch.setattr("app.conversion.libreoffice_engine.run_process", fake_run_process)
    monkeypatch.setattr(
        "app.conversion.libreoffice_engine.html_to_markdown",
        lambda _html: ("Line\r\n", []),
    )

    engine = LibreOfficeEngine(settings=_settings())
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.CONVERTED_WITH_WARNINGS
    assert output.read_text(encoding="utf-8") == "Line\n"
    assert any(item.code == "DOC_INTERMEDIATE_DOCX" for item in result.warnings)


def test_convert_rtf_uses_direct_html_export(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "notes.rtf"
    source.write_text(r"{\rtf1\ansi Notes}", encoding="utf-8")
    output = tmp_path / "notes.md"
    seen_targets: list[str] = []

    def fake_detect(_: AppSettings) -> DependencyStatus:
        return DependencyStatus(name="libreoffice", available=True, path="soffice")

    def fake_run_process(command: list[str], timeout_seconds: int) -> ProcessRunResult:
        assert timeout_seconds == 180
        out_dir = Path(command[command.index("--outdir") + 1])
        out_dir.mkdir(parents=True, exist_ok=True)
        target = command[command.index("--convert-to") + 1]
        seen_targets.append(target)
        if target == "html":
            (out_dir / f"{source.stem}.html").write_text("<p>Notes</p>", encoding="utf-8")
        return ProcessRunResult(returncode=0, stdout="", stderr="", timed_out=False)

    monkeypatch.setattr("app.conversion.libreoffice_engine.detect_libreoffice", fake_detect)
    monkeypatch.setattr("app.conversion.libreoffice_engine.run_process", fake_run_process)
    monkeypatch.setattr(
        "app.conversion.libreoffice_engine.html_to_markdown",
        lambda _html: ("Notes\r\n", []),
    )

    engine = LibreOfficeEngine(settings=_settings())
    result = engine.convert(source, output, _plan(source, output))

    assert seen_targets == ["html"]
    assert result.status == FileStatus.CONVERTED
    assert output.read_text(encoding="utf-8") == "Notes\n"
    assert result.metadata["route"] == "libreoffice->html->markdown"
