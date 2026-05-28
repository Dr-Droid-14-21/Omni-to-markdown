from pathlib import Path

from app.conversion.service import ConversionService
from app.core.models import ConversionError, ConversionResult, FileStatus, Severity
from app.core.settings import AppSettings


def _settings() -> AppSettings:
    return AppSettings.default()


def test_conversion_service_uses_pandoc_for_docx(tmp_path: Path) -> None:
    source = tmp_path / "input.docx"
    source.write_bytes(b"PK")
    output_dir = tmp_path / "out"

    service = ConversionService(settings=_settings())

    def fake_convert(source_path: Path, output_path: Path, _: object) -> ConversionResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("ok\n", encoding="utf-8")
        return ConversionResult(
            source_path=source_path,
            output_path=output_path,
            engine_name="pandoc",
            status=FileStatus.CONVERTED,
        )

    service.pandoc_engine.convert = fake_convert  # type: ignore[method-assign]
    service.pandoc_engine.can_convert = lambda *_: True  # type: ignore[method-assign]
    results = service.convert_files([source], output_dir)

    assert len(results) == 1
    assert results[0].status == FileStatus.CONVERTED
    assert (output_dir / "input.md").exists()


def test_conversion_service_marks_unavailable_engines_as_failed(tmp_path: Path) -> None:
    source = tmp_path / "scan.pdf"
    source.write_bytes(b"%PDF-1.7")
    output_dir = tmp_path / "out"

    service = ConversionService(settings=_settings())
    service.pymupdf_engine.can_convert = lambda *_: False  # type: ignore[method-assign]
    service.pdfminer_engine.can_convert = lambda *_: False  # type: ignore[method-assign]
    results = service.convert_files([source], output_dir)

    assert results[0].status == FileStatus.FAILED
    assert results[0].errors[0].code == "ENGINE_NOT_AVAILABLE"


def test_conversion_service_avoids_output_name_conflicts(tmp_path: Path) -> None:
    source = tmp_path / "input.docx"
    source.write_bytes(b"PK")
    output_dir = tmp_path / "out"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "input.md").write_text("existing\n", encoding="utf-8")

    service = ConversionService(settings=_settings())

    def fake_convert(source_path: Path, output_path: Path, _: object) -> ConversionResult:
        output_path.write_text("new\n", encoding="utf-8")
        return ConversionResult(
            source_path=source_path,
            output_path=output_path,
            engine_name="pandoc",
            status=FileStatus.CONVERTED,
        )

    service.pandoc_engine.convert = fake_convert  # type: ignore[method-assign]
    service.pandoc_engine.can_convert = lambda *_: True  # type: ignore[method-assign]
    results = service.convert_files([source], output_dir)

    assert results[0].output_path is not None
    assert results[0].output_path.name == "input (1).md"


def test_conversion_service_emits_progress_callback(tmp_path: Path) -> None:
    first = tmp_path / "a.docx"
    second = tmp_path / "b.docx"
    first.write_bytes(b"PK")
    second.write_bytes(b"PK")
    output_dir = tmp_path / "out"

    service = ConversionService(settings=_settings())

    def fake_convert(source_path: Path, output_path: Path, _: object) -> ConversionResult:
        output_path.write_text("ok\n", encoding="utf-8")
        return ConversionResult(
            source_path=source_path,
            output_path=output_path,
            engine_name="pandoc",
            status=FileStatus.CONVERTED,
        )

    events: list[tuple[int, int, str]] = []

    def on_progress(index: int, total: int, result: ConversionResult) -> None:
        events.append((index, total, result.source_path.name))

    service.pandoc_engine.convert = fake_convert  # type: ignore[method-assign]
    service.pandoc_engine.can_convert = lambda *_: True  # type: ignore[method-assign]
    service.convert_files([first, second], output_dir, progress_callback=on_progress)

    assert events == [(1, 2, "a.docx"), (2, 2, "b.docx")]


def test_conversion_service_uses_mammoth_fallback_when_pandoc_fails(tmp_path: Path) -> None:
    source = tmp_path / "input.docx"
    source.write_bytes(b"PK")
    output_dir = tmp_path / "out"

    service = ConversionService(settings=_settings())

    def failed_pandoc(source_path: Path, output_path: Path, _: object) -> ConversionResult:
        return ConversionResult(
            source_path=source_path,
            output_path=output_path,
            engine_name="pandoc",
            status=FileStatus.FAILED,
            errors=[
                ConversionError(
                    code="PANDOC_FAILED",
                    severity=Severity.ERROR,
                    title="Pandoc failed",
                    message="bad input",
                )
            ],
        )

    def succeeded_mammoth(source_path: Path, output_path: Path, _: object) -> ConversionResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("ok\n", encoding="utf-8")
        return ConversionResult(
            source_path=source_path,
            output_path=output_path,
            engine_name="mammoth",
            status=FileStatus.CONVERTED,
        )

    service.pandoc_engine.can_convert = lambda *_: True  # type: ignore[method-assign]
    service.pandoc_engine.convert = failed_pandoc  # type: ignore[method-assign]
    service.mammoth_engine.can_convert = lambda *_: True  # type: ignore[method-assign]
    service.mammoth_engine.convert = succeeded_mammoth  # type: ignore[method-assign]

    results = service.convert_files([source], output_dir)

    assert results[0].status == FileStatus.CONVERTED
    assert results[0].engine_name == "mammoth"
    assert any(item.code == "FALLBACK_ENGINE_USED" for item in results[0].warnings)


def test_conversion_service_uses_pdfminer_fallback_when_pymupdf_fails(tmp_path: Path) -> None:
    source = tmp_path / "scan.pdf"
    source.write_bytes(b"%PDF-1.7")
    output_dir = tmp_path / "out"

    service = ConversionService(settings=_settings())

    def failed_pymupdf(source_path: Path, output_path: Path, _: object) -> ConversionResult:
        return ConversionResult(
            source_path=source_path,
            output_path=output_path,
            engine_name="pymupdf",
            status=FileStatus.FAILED,
            errors=[
                ConversionError(
                    code="PDF_OPEN_FAILED",
                    severity=Severity.ERROR,
                    title="PDF open failed",
                    message="bad pdf",
                )
            ],
        )

    def succeeded_pdfminer(source_path: Path, output_path: Path, _: object) -> ConversionResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("ok\n", encoding="utf-8")
        return ConversionResult(
            source_path=source_path,
            output_path=output_path,
            engine_name="pdfminer",
            status=FileStatus.CONVERTED,
        )

    service.pymupdf_engine.can_convert = lambda *_: True  # type: ignore[method-assign]
    service.pymupdf_engine.convert = failed_pymupdf  # type: ignore[method-assign]
    service.pdfminer_engine.can_convert = lambda *_: True  # type: ignore[method-assign]
    service.pdfminer_engine.convert = succeeded_pdfminer  # type: ignore[method-assign]

    results = service.convert_files([source], output_dir)

    assert results[0].status == FileStatus.CONVERTED
    assert results[0].engine_name == "pdfminer"
    assert any(item.code == "FALLBACK_ENGINE_USED" for item in results[0].warnings)


def test_conversion_service_marks_remaining_as_cancelled_when_requested(tmp_path: Path) -> None:
    first = tmp_path / "a.docx"
    second = tmp_path / "b.docx"
    first.write_bytes(b"PK")
    second.write_bytes(b"PK")
    output_dir = tmp_path / "out"

    service = ConversionService(settings=_settings())

    def succeeded_pandoc(source_path: Path, output_path: Path, _: object) -> ConversionResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("ok\n", encoding="utf-8")
        return ConversionResult(
            source_path=source_path,
            output_path=output_path,
            engine_name="pandoc",
            status=FileStatus.CONVERTED,
        )

    cancel_checks = {"count": 0}

    def should_cancel() -> bool:
        cancel_checks["count"] += 1
        return cancel_checks["count"] >= 2

    service.pandoc_engine.can_convert = lambda *_: True  # type: ignore[method-assign]
    service.pandoc_engine.convert = succeeded_pandoc  # type: ignore[method-assign]

    results = service.convert_files([first, second], output_dir, should_cancel=should_cancel)

    assert results[0].status == FileStatus.CONVERTED
    assert results[1].status == FileStatus.CANCELLED
    assert any(item.code == "CANCELLED_BY_USER" for item in results[1].warnings)
