from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import pytest

from app.conversion.libreoffice_engine import LibreOfficeEngine
from app.core.models import ConversionPlan, FileStatus
from app.core.settings import AppSettings

_LIBREOFFICE_BINARY = shutil.which("soffice") or shutil.which("libreoffice")

pytestmark = pytest.mark.skipif(
    _LIBREOFFICE_BINARY is None,
    reason="LibreOffice not available on PATH",
)


def test_libreoffice_engine_converts_docx_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "seed.docx"
    output = tmp_path / "out.md"
    _write_minimal_docx(source, "Hello LibreOffice")

    settings = AppSettings.default()
    settings.libreoffice_binary_path = _LIBREOFFICE_BINARY or ""
    engine = LibreOfficeEngine(settings=settings, timeout_seconds=120)
    plan = ConversionPlan(
        source_path=source,
        output_path=output,
        detected_extension=".docx",
        preferred_engine="libreoffice",
    )

    result = engine.convert(source, output, plan)

    assert result.status in {FileStatus.CONVERTED, FileStatus.CONVERTED_WITH_WARNINGS}
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "Hello LibreOffice" in content


def _write_minimal_docx(path: Path, text: str) -> None:
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml"
            ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""
    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
                Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
                Target="word/document.xml"/>
</Relationships>
"""
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r>
        <w:t>{text}</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>
"""
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document_xml)
