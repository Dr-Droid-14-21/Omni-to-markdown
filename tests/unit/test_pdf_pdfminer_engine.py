from pathlib import Path

from app.conversion.pdf_pdfminer_engine import PDFMinerEngine
from app.core.models import ConversionPlan, FileStatus


def _plan(source: Path, output: Path) -> ConversionPlan:
    return ConversionPlan(
        source_path=source,
        output_path=output,
        detected_extension=source.suffix.lower(),
        preferred_engine="pdfminer",
    )


def test_is_available_false_when_package_missing(monkeypatch: object) -> None:
    monkeypatch.setattr("app.conversion.pdf_pdfminer_engine._load_extract_text", lambda: None)
    engine = PDFMinerEngine()
    assert engine.is_available().available is False


def test_convert_fails_for_unsupported_extension(tmp_path: Path) -> None:
    source = tmp_path / "a.docx"
    source.write_text("", encoding="utf-8")
    output = tmp_path / "a.md"

    engine = PDFMinerEngine()
    result = engine.convert(source, output, _plan(source, output))
    assert result.status == FileStatus.FAILED
    assert result.errors[0].code == "UNSUPPORTED_EXTENSION"


def test_convert_success_writes_markdown(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "a.pdf"
    source.write_bytes(b"%PDF-1.7")
    output = tmp_path / "a.md"

    monkeypatch.setattr(
        "app.conversion.pdf_pdfminer_engine._load_extract_text",
        lambda: (lambda _path: "Line A\r\nLine B"),
    )

    engine = PDFMinerEngine()
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.CONVERTED
    assert output.read_text(encoding="utf-8") == "Line A\nLine B\n"


def test_convert_warns_for_empty_text_layer(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "a.pdf"
    source.write_bytes(b"%PDF-1.7")
    output = tmp_path / "a.md"

    monkeypatch.setattr(
        "app.conversion.pdf_pdfminer_engine._load_extract_text",
        lambda: (lambda _path: ""),
    )

    engine = PDFMinerEngine()
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.CONVERTED_WITH_WARNINGS
    assert result.warnings[0].code == "PDF_NO_TEXT_LAYER"
