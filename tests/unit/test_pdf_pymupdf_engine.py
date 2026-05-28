from pathlib import Path
from types import SimpleNamespace

from app.conversion.pdf_pymupdf_engine import PyMuPDFEngine
from app.core.models import ConversionPlan, FileStatus


def _plan(source: Path, output: Path) -> ConversionPlan:
    return ConversionPlan(
        source_path=source,
        output_path=output,
        detected_extension=source.suffix.lower(),
        preferred_engine="pymupdf",
    )


def test_is_available_false_when_package_missing(monkeypatch: object) -> None:
    monkeypatch.setattr("app.conversion.pdf_pymupdf_engine._load_pymupdf_module", lambda: None)
    engine = PyMuPDFEngine()
    assert engine.is_available().available is False


def test_convert_fails_for_unsupported_extension(tmp_path: Path) -> None:
    source = tmp_path / "a.docx"
    source.write_text("", encoding="utf-8")
    output = tmp_path / "a.md"

    engine = PyMuPDFEngine()
    result = engine.convert(source, output, _plan(source, output))
    assert result.status == FileStatus.FAILED
    assert result.errors[0].code == "UNSUPPORTED_EXTENSION"


def test_convert_success_writes_markdown(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "a.pdf"
    source.write_bytes(b"%PDF-1.7")
    output = tmp_path / "a.md"

    class FakePage:
        def get_text(self, _mode: str) -> str:
            return "Line 1\n"

        def get_images(self, full: bool = True) -> list[object]:
            assert full is True
            return []

    class FakeDocument:
        needs_pass = False

        def __len__(self) -> int:
            return 1

        def __iter__(self):
            return iter([FakePage()])

        def close(self) -> None:
            return

    fake_module = SimpleNamespace(open=lambda _path: FakeDocument())
    monkeypatch.setattr(
        "app.conversion.pdf_pymupdf_engine._load_pymupdf_module",
        lambda: fake_module,
    )

    engine = PyMuPDFEngine()
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.CONVERTED
    assert output.read_text(encoding="utf-8") == "Line 1\n"


def test_convert_warns_when_no_text_layer(tmp_path: Path, monkeypatch: object) -> None:
    source = tmp_path / "a.pdf"
    source.write_bytes(b"%PDF-1.7")
    output = tmp_path / "a.md"

    class FakePage:
        def get_text(self, _mode: str) -> str:
            return ""

        def get_images(self, full: bool = True) -> list[object]:
            assert full is True
            return [object()]

    class FakeDocument:
        needs_pass = False

        def __len__(self) -> int:
            return 1

        def __iter__(self):
            return iter([FakePage()])

        def close(self) -> None:
            return

    fake_module = SimpleNamespace(open=lambda _path: FakeDocument())
    monkeypatch.setattr(
        "app.conversion.pdf_pymupdf_engine._load_pymupdf_module",
        lambda: fake_module,
    )

    engine = PyMuPDFEngine()
    result = engine.convert(source, output, _plan(source, output))

    assert result.status == FileStatus.CONVERTED_WITH_WARNINGS
    codes = {item.code for item in result.warnings}
    assert "PDF_NO_TEXT_LAYER" in codes
    assert "PDF_IMAGE_HEAVY_PAGES" in codes
