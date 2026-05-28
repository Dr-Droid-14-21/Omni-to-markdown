from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from app.conversion.pandoc_engine import PandocEngine
from app.core.models import ConversionPlan, FileStatus
from app.core.settings import AppSettings

pytestmark = pytest.mark.skipif(
    shutil.which("pandoc") is None,
    reason="pandoc not available on PATH",
)


def test_pandoc_engine_converts_docx_roundtrip(tmp_path: Path) -> None:
    markdown_source = tmp_path / "seed.md"
    markdown_source.write_text("# Title\n\nParagraph\n", encoding="utf-8")
    docx_source = tmp_path / "seed.docx"
    output_md = tmp_path / "out.md"

    subprocess.run(
        [
            "pandoc",
            str(markdown_source),
            "--from=gfm",
            "--to=docx",
            "--output",
            str(docx_source),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    settings = AppSettings.default()
    settings.pandoc_binary_path = ""
    engine = PandocEngine(settings=settings)
    plan = ConversionPlan(
        source_path=docx_source,
        output_path=output_md,
        detected_extension=".docx",
        preferred_engine="pandoc",
    )

    result = engine.convert(docx_source, output_md, plan)

    assert result.status == FileStatus.CONVERTED
    assert output_md.exists()
    content = output_md.read_text(encoding="utf-8")
    assert "Title" in content
    assert "Paragraph" in content
