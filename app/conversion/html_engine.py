from __future__ import annotations

import time
from pathlib import Path

from app.conversion.base import ConversionEngine, EngineAvailability
from app.conversion.html_to_markdown import html_to_markdown
from app.conversion.markdown_normalizer import normalize_markdown_file
from app.core.models import ConversionPlan, ConversionResult, FileStatus


class HtmlEngine(ConversionEngine):
    name = "html"
    supported_extensions = {".html", ".htm"}

    def is_available(self) -> EngineAvailability:
        return EngineAvailability(available=True)

    def can_convert(self, source: Path, plan: ConversionPlan) -> bool:
        return source.suffix.lower() in self.supported_extensions

    def convert(self, source: Path, output: Path, plan: ConversionPlan) -> ConversionResult:
        start = time.monotonic()
        html = source.read_text(encoding="utf-8", errors="replace")
        markdown, warnings = html_to_markdown(html)

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown.strip() + "\n", encoding="utf-8")
        normalize_markdown_file(output)

        return ConversionResult(
            source_path=source,
            output_path=output,
            engine_name=self.name,
            status=FileStatus.CONVERTED_WITH_WARNINGS if warnings else FileStatus.CONVERTED,
            warnings=warnings,
            duration_ms=int((time.monotonic() - start) * 1000),
        )
