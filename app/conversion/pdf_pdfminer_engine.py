from __future__ import annotations

import time
from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from typing import Any

from app.conversion.base import ConversionEngine, EngineAvailability
from app.conversion.markdown_normalizer import normalize_markdown_text
from app.core.models import (
    ConversionError,
    ConversionPlan,
    ConversionResult,
    ConversionWarning,
    FileStatus,
    Severity,
)


class PDFMinerEngine(ConversionEngine):
    name = "pdfminer"
    supported_extensions = {".pdf"}

    def is_available(self) -> EngineAvailability:
        if _load_extract_text() is None:
            return EngineAvailability(
                available=False,
                reason="Python package `pdfminer.six` is not installed.",
            )
        return EngineAvailability(available=True)

    def can_convert(self, source: Path, plan: ConversionPlan) -> bool:
        return source.suffix.lower() in self.supported_extensions and self.is_available().available

    def convert(self, source: Path, output: Path, plan: ConversionPlan) -> ConversionResult:
        start = time.monotonic()
        if source.suffix.lower() not in self.supported_extensions:
            return _failure_result(
                source=source,
                output=output,
                code="UNSUPPORTED_EXTENSION",
                title="pdfminer route unsupported",
                message=f"pdfminer engine does not support {source.suffix.lower()}.",
                start=start,
                engine_name=self.name,
            )

        extract_text = _load_extract_text()
        if extract_text is None:
            return _failure_result(
                source=source,
                output=output,
                code="PDFMINER_NOT_FOUND",
                title="pdfminer not available",
                message="Install `pdfminer.six` to enable PDF fallback extraction.",
                start=start,
                engine_name=self.name,
            )

        try:
            text = str(extract_text(str(source)) or "")
        except Exception as exc:  # noqa: BLE001
            message = str(exc)
            code = (
                "PDF_PASSWORD_PROTECTED"
                if _looks_like_password_error(message)
                else "PDF_EXTRACT_FAILED"
            )
            title = (
                "Password-protected PDF"
                if code == "PDF_PASSWORD_PROTECTED"
                else "PDF extraction failed"
            )
            return _failure_result(
                source=source,
                output=output,
                code=code,
                title=title,
                message=message,
                start=start,
                engine_name=self.name,
            )

        warnings: list[ConversionWarning] = []
        trimmed = text.strip()
        if not trimmed:
            warnings.append(
                ConversionWarning(
                    code="PDF_NO_TEXT_LAYER",
                    message=(
                        "No extractable text layer was found in this PDF. "
                        "The file may be scanned images."
                    ),
                )
            )

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(normalize_markdown_text(trimmed), encoding="utf-8", newline="\n")

        status = FileStatus.CONVERTED_WITH_WARNINGS if warnings else FileStatus.CONVERTED
        return ConversionResult(
            source_path=source,
            output_path=output,
            engine_name=self.name,
            status=status,
            warnings=warnings,
            duration_ms=int((time.monotonic() - start) * 1000),
            metadata={"character_count": str(len(trimmed))},
        )


def _load_extract_text() -> Callable[..., Any] | None:
    try:
        module = import_module("pdfminer.high_level")
    except ImportError:
        return None
    extract_text = getattr(module, "extract_text", None)
    if callable(extract_text):
        return extract_text
    return None


def _failure_result(
    *,
    source: Path,
    output: Path,
    code: str,
    title: str,
    message: str,
    start: float,
    engine_name: str,
) -> ConversionResult:
    return ConversionResult(
        source_path=source,
        output_path=output,
        engine_name=engine_name,
        status=FileStatus.FAILED,
        duration_ms=int((time.monotonic() - start) * 1000),
        errors=[
            ConversionError(
                code=code,
                severity=Severity.ERROR,
                title=title,
                message=message,
            )
        ],
    )


def _looks_like_password_error(message: str) -> bool:
    lowered = message.lower()
    return "password" in lowered or "encrypted" in lowered
