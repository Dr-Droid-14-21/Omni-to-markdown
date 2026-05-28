from __future__ import annotations

import time
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from app.conversion.base import ConversionEngine, EngineAvailability
from app.conversion.html_to_markdown import html_to_markdown
from app.conversion.markdown_normalizer import normalize_markdown_text
from app.core.models import (
    ConversionError,
    ConversionPlan,
    ConversionResult,
    ConversionWarning,
    FileStatus,
    Severity,
)
from app.core.settings import AppSettings, load_settings


class MammothEngine(ConversionEngine):
    name = "mammoth"
    supported_extensions = {".docx"}

    def __init__(
        self,
        settings: AppSettings | None = None,
        style_map: str | None = None,
    ) -> None:
        self.settings = settings or load_settings()
        self.style_map = style_map

    def is_available(self) -> EngineAvailability:
        module = _load_mammoth_module()
        if module is None:
            return EngineAvailability(
                available=False,
                reason="Python package `mammoth` is not installed.",
            )
        return EngineAvailability(available=True)

    def can_convert(self, source: Path, plan: ConversionPlan) -> bool:
        return source.suffix.lower() in self.supported_extensions and self.is_available().available

    def convert(self, source: Path, output: Path, plan: ConversionPlan) -> ConversionResult:
        start = time.monotonic()
        extension = source.suffix.lower()
        if extension not in self.supported_extensions:
            return self._failure_result(
                source=source,
                output=output,
                code="UNSUPPORTED_EXTENSION",
                title="Mammoth route unsupported",
                message=f"Mammoth engine does not support {extension}.",
                start=start,
            )

        module = _load_mammoth_module()
        if module is None:
            return self._failure_result(
                source=source,
                output=output,
                code="MAMMOTH_NOT_FOUND",
                title="Mammoth not available",
                message="Install the `mammoth` package to enable this route.",
                start=start,
            )

        try:
            with source.open("rb") as docx_file:
                kwargs: dict[str, Any] = {}
                if self.style_map:
                    kwargs["style_map"] = self.style_map
                mammoth_result = module.convert_to_html(docx_file, **kwargs)
        except OSError as exc:
            return self._failure_result(
                source=source,
                output=output,
                code="MAMMOTH_READ_ERROR",
                title="Input read failed",
                message=str(exc),
                start=start,
            )
        except Exception as exc:
            return self._failure_result(
                source=source,
                output=output,
                code="MAMMOTH_CONVERT_ERROR",
                title="Mammoth conversion failed",
                message=str(exc),
                start=start,
            )

        html = str(getattr(mammoth_result, "value", ""))
        markdown, warnings = html_to_markdown(html)
        warnings.extend(_warnings_from_mammoth_messages(getattr(mammoth_result, "messages", [])))

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(normalize_markdown_text(markdown), encoding="utf-8", newline="\n")

        status = FileStatus.CONVERTED_WITH_WARNINGS if warnings else FileStatus.CONVERTED
        return ConversionResult(
            source_path=source,
            output_path=output,
            engine_name=self.name,
            status=status,
            warnings=warnings,
            duration_ms=int((time.monotonic() - start) * 1000),
            metadata={"route": "docx->html->markdown"},
        )

    def _failure_result(
        self,
        *,
        source: Path,
        output: Path,
        code: str,
        title: str,
        message: str,
        start: float,
    ) -> ConversionResult:
        return ConversionResult(
            source_path=source,
            output_path=output,
            engine_name=self.name,
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


def _load_mammoth_module() -> ModuleType | None:
    try:
        module = import_module("mammoth")
    except ImportError:
        return None
    return module


def _warnings_from_mammoth_messages(messages: list[Any]) -> list[ConversionWarning]:
    warnings: list[ConversionWarning] = []
    for message in messages:
        text = str(getattr(message, "message", "")).strip()
        if not text:
            continue
        warning_type = str(getattr(message, "type", "warning")).lower()
        warnings.append(
            ConversionWarning(
                code="MAMMOTH_MESSAGE",
                message=text,
                detail=f"type={warning_type}",
            )
        )
    return warnings
