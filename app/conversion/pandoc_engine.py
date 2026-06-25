from __future__ import annotations

import subprocess
import time
from pathlib import Path

from app.conversion.base import ConversionEngine, EngineAvailability
from app.conversion.dependency_check import detect_pandoc
from app.conversion.markdown_normalizer import normalize_markdown_file
from app.core.models import (
    ConversionError,
    ConversionPlan,
    ConversionResult,
    FileStatus,
    Severity,
)
from app.core.settings import AppSettings, load_settings


class PandocEngine(ConversionEngine):
    name = "pandoc"
    supported_extensions = {".docx", ".htm", ".html", ".odt"}

    def __init__(self, settings: AppSettings | None = None, timeout_seconds: int = 120) -> None:
        self.settings = settings or load_settings()
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> EngineAvailability:
        status = detect_pandoc(self.settings)
        return EngineAvailability(available=status.available, reason=status.detail)

    def can_convert(self, source: Path, plan: ConversionPlan) -> bool:
        return source.suffix.lower() in self.supported_extensions and self.is_available().available

    def convert(self, source: Path, output: Path, plan: ConversionPlan) -> ConversionResult:
        start = time.monotonic()
        source_extension = source.suffix.lower()

        if source_extension not in self.supported_extensions:
            return self._failure_result(
                source=source,
                output=output,
                code="UNSUPPORTED_EXTENSION",
                title="Pandoc route unsupported",
                message=f"Pandoc engine does not support {source_extension}.",
                start=start,
            )

        pandoc_status = detect_pandoc(self.settings)
        if not pandoc_status.available:
            return self._failure_result(
                source=source,
                output=output,
                code="PANDOC_NOT_FOUND",
                title="Pandoc not available",
                message=pandoc_status.detail or "Pandoc executable not found.",
                start=start,
            )

        output.parent.mkdir(parents=True, exist_ok=True)
        pandoc_path = pandoc_status.path or "pandoc"
        from_format = _source_format_for_extension(source_extension)
        command = [
            pandoc_path,
            str(source),
            f"--from={from_format}",
            "--to=gfm",
            "--wrap=none",
            "--output",
            str(output),
        ]

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return self._failure_result(
                source=source,
                output=output,
                code="PANDOC_TIMEOUT",
                title="Pandoc timeout",
                message=f"Pandoc timed out after {self.timeout_seconds} seconds.",
                start=start,
            )
        except OSError as exc:
            return self._failure_result(
                source=source,
                output=output,
                code="PANDOC_EXEC_ERROR",
                title="Pandoc execution error",
                message=str(exc),
                start=start,
            )

        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            detail = stderr if stderr else "Pandoc returned a non-zero exit code."
            return self._failure_result(
                source=source,
                output=output,
                code="PANDOC_FAILED",
                title="Pandoc failed",
                message=detail,
                start=start,
            )

        if not output.exists():
            return self._failure_result(
                source=source,
                output=output,
                code="OUTPUT_MISSING",
                title="Output missing",
                message="Pandoc completed but no output markdown file was created.",
                start=start,
            )

        normalize_markdown_file(output)
        return ConversionResult(
            source_path=source,
            output_path=output,
            engine_name=self.name,
            status=FileStatus.CONVERTED,
            duration_ms=int((time.monotonic() - start) * 1000),
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


def _source_format_for_extension(extension: str) -> str:
    mapping = {
        ".docx": "docx",
        ".htm": "html",
        ".odt": "odt",
        ".html": "html",
    }
    return mapping.get(extension, "markdown")
