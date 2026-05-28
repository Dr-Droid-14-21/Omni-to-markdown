from pathlib import Path
from types import SimpleNamespace

from app.conversion.mammoth_engine import MammothEngine
from app.core.models import ConversionPlan, ConversionWarning, FileStatus
from app.core.settings import AppSettings


def _settings() -> AppSettings:
    return AppSettings.default()


def _plan(source: Path, output: Path) -> ConversionPlan:
    return ConversionPlan(
        source_path=source,
        output_path=output,
        detected_extension=source.suffix.lower(),
        preferred_engine="mammoth",
    )


def test_is_available_false_when_mammoth_missing(monkeypatch: object) -> None:
    monkeypatch.setattr("app.conversion.mammoth_engine._load_mammoth_module", lambda: None)
    engine = MammothEngine(settings=_settings())

    assert engine.is_available().available is False


def test_convert_fails_for_unsupported_extension(tmp_path: Path) -> None:
    source = tmp_path / "a.pdf"
    source.write_bytes(b"%PDF-1.7")
    output = tmp_path / "a.md"

    engine = MammothEngine(settings=_settings())
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.FAILED
    assert result.errors[0].code == "UNSUPPORTED_EXTENSION"


def test_convert_fails_when_mammoth_package_missing(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "a.docx"
    source.write_bytes(b"PK")
    output = tmp_path / "a.md"

    monkeypatch.setattr("app.conversion.mammoth_engine._load_mammoth_module", lambda: None)

    engine = MammothEngine(settings=_settings())
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.FAILED
    assert result.errors[0].code == "MAMMOTH_NOT_FOUND"


def test_convert_success_writes_normalized_output(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "a.docx"
    source.write_bytes(b"PK")
    output = tmp_path / "a.md"

    fake_module = SimpleNamespace(
        convert_to_html=lambda *_args, **_kwargs: SimpleNamespace(
            value="<p>Line 1</p>",
            messages=[SimpleNamespace(type="warning", message="minor styling difference")],
        )
    )
    monkeypatch.setattr(
        "app.conversion.mammoth_engine._load_mammoth_module",
        lambda: fake_module,
    )
    monkeypatch.setattr(
        "app.conversion.mammoth_engine.html_to_markdown",
        lambda _html: (
            "Line 1\r\n",
            [ConversionWarning(code="HTML_NOTE", message="html warning")],
        ),
    )

    engine = MammothEngine(settings=_settings())
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.CONVERTED_WITH_WARNINGS
    assert output.read_text(encoding="utf-8") == "Line 1\n"
    assert any(item.code == "MAMMOTH_MESSAGE" for item in result.warnings)
