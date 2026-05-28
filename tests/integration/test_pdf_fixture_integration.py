from __future__ import annotations

from pathlib import Path

import pytest

from app.conversion.pdf_pdfminer_engine import PDFMinerEngine
from app.conversion.pdf_pymupdf_engine import PyMuPDFEngine
from app.core.models import ConversionPlan, FileStatus

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample.pdf"


def _plan(source: Path, output: Path, engine_name: str) -> ConversionPlan:
    return ConversionPlan(
        source_path=source,
        output_path=output,
        detected_extension=".pdf",
        preferred_engine=engine_name,
    )


def test_pymupdf_converts_safe_pdf_fixture(tmp_path: Path) -> None:
    engine = PyMuPDFEngine()
    if not engine.is_available().available:
        pytest.skip("pymupdf not available")

    output = tmp_path / "sample-pymupdf.md"
    result = engine.convert(FIXTURE, output, _plan(FIXTURE, output, "pymupdf"))

    assert result.status == FileStatus.CONVERTED
    assert result.metadata["page_count"] == "1"
    content = output.read_text(encoding="utf-8")
    assert "# Sample Document" in content
    assert "Omni to Markdown converter" in content


def test_pdfminer_converts_safe_pdf_fixture(tmp_path: Path) -> None:
    engine = PDFMinerEngine()
    if not engine.is_available().available:
        pytest.skip("pdfminer.six not available")

    output = tmp_path / "sample-pdfminer.md"
    result = engine.convert(FIXTURE, output, _plan(FIXTURE, output, "pdfminer"))

    assert result.status == FileStatus.CONVERTED
    content = output.read_text(encoding="utf-8")
    assert "# Sample Document" in content
    assert "Omni to Markdown converter" in content
