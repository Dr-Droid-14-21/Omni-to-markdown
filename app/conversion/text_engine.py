from __future__ import annotations

import time
from pathlib import Path

from app.conversion.base import ConversionEngine, EngineAvailability
from app.conversion.markdown_normalizer import normalize_markdown_text
from app.core.models import ConversionPlan, ConversionResult, FileStatus


class TextEngine(ConversionEngine):
    name = "text"
    supported_extensions = {".txt"}

    def is_available(self) -> EngineAvailability:
        return EngineAvailability(available=True)

    def can_convert(self, source: Path, plan: ConversionPlan) -> bool:
        return source.suffix.lower() in self.supported_extensions

    def convert(self, source: Path, output: Path, plan: ConversionPlan) -> ConversionResult:
        start = time.monotonic()
        text = source.read_text(encoding="utf-8", errors="replace")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(normalize_markdown_text(text), encoding="utf-8", newline="\n")
        return ConversionResult(
            source_path=source,
            output_path=output,
            engine_name=self.name,
            status=FileStatus.CONVERTED,
            duration_ms=int((time.monotonic() - start) * 1000),
        )
