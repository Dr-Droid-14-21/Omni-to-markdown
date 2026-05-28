from pathlib import Path
from types import SimpleNamespace

from app.conversion.dependency_check import DependencyStatus
from app.conversion.pandoc_engine import PandocEngine
from app.core.models import ConversionPlan, FileStatus
from app.core.settings import AppSettings


def _settings() -> AppSettings:
    cfg = AppSettings.default()
    cfg.pandoc_binary_path = ""
    return cfg


def _plan(source: Path, output: Path) -> ConversionPlan:
    return ConversionPlan(
        source_path=source,
        output_path=output,
        detected_extension=source.suffix.lower(),
        preferred_engine="pandoc",
    )


def test_is_available_when_pandoc_found(monkeypatch: object) -> None:
    def fake_detect(_: AppSettings) -> DependencyStatus:
        return DependencyStatus(name="pandoc", available=True, path=r"C:\pandoc.exe")

    monkeypatch.setattr("app.conversion.pandoc_engine.detect_pandoc", fake_detect)
    engine = PandocEngine(settings=_settings())

    assert engine.is_available().available is True


def test_convert_fails_for_unsupported_extension(tmp_path: Path) -> None:
    source = tmp_path / "a.pdf"
    source.write_bytes(b"%PDF-1.7")
    output = tmp_path / "a.md"

    engine = PandocEngine(settings=_settings())
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.FAILED
    assert result.errors[0].code == "UNSUPPORTED_EXTENSION"


def test_convert_success_writes_normalized_output(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "a.docx"
    source.write_bytes(b"PK")
    output = tmp_path / "a.md"

    def fake_detect(_: AppSettings) -> DependencyStatus:
        return DependencyStatus(name="pandoc", available=True, path="pandoc")

    def fake_run(command: list[str], **_: object) -> SimpleNamespace:
        assert "--to=gfm" in command
        out_idx = command.index("--output") + 1
        Path(command[out_idx]).write_bytes(b"line1  \r\nline2\r\n")
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr("app.conversion.pandoc_engine.detect_pandoc", fake_detect)
    monkeypatch.setattr("subprocess.run", fake_run)
    engine = PandocEngine(settings=_settings())
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.CONVERTED
    assert output.read_text(encoding="utf-8") == "line1\nline2\n"


def test_convert_handles_pandoc_failure(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "a.docx"
    source.write_bytes(b"PK")
    output = tmp_path / "a.md"

    def fake_detect(_: AppSettings) -> DependencyStatus:
        return DependencyStatus(name="pandoc", available=True, path="pandoc")

    def fake_run(*_: object, **__: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=2, stderr="bad input")

    monkeypatch.setattr("app.conversion.pandoc_engine.detect_pandoc", fake_detect)
    monkeypatch.setattr("subprocess.run", fake_run)

    engine = PandocEngine(settings=_settings())
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.FAILED
    assert result.errors[0].code == "PANDOC_FAILED"
