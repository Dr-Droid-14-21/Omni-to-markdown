from __future__ import annotations

import tempfile
import time
from pathlib import Path

from app.conversion.base import ConversionEngine, EngineAvailability
from app.conversion.dependency_check import detect_libreoffice
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
from app.core.process import run_process
from app.core.settings import AppSettings, load_settings


class LibreOfficeEngine(ConversionEngine):
    name = "libreoffice"
    supported_extensions = {".doc", ".docx", ".odt", ".odf", ".rtf"}

    def __init__(self, settings: AppSettings | None = None, timeout_seconds: int = 180) -> None:
        self.settings = settings or load_settings()
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> EngineAvailability:
        status = detect_libreoffice(self.settings)
        return EngineAvailability(available=status.available, reason=status.detail)

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
                title="LibreOffice route unsupported",
                message=f"LibreOffice engine does not support {extension}.",
                start=start,
            )

        libreoffice_status = detect_libreoffice(self.settings)
        if not libreoffice_status.available:
            return self._failure_result(
                source=source,
                output=output,
                code="LIBREOFFICE_NOT_FOUND",
                title="LibreOffice not available",
                message=libreoffice_status.detail or "LibreOffice executable not found.",
                start=start,
            )

        binary = libreoffice_status.path or "soffice"
        warnings: list[ConversionWarning] = []
        try:
            with tempfile.TemporaryDirectory(prefix="omni-lo-profile-") as profile_dir:
                with tempfile.TemporaryDirectory(prefix="omni-lo-export-") as export_dir:
                    profile_uri = Path(profile_dir).resolve().as_uri()
                    export_path = Path(export_dir)
                    html_source = source

                    if extension == ".doc":
                        docx_command = _build_convert_command(
                            binary=binary,
                            profile_uri=profile_uri,
                            source=source,
                            outdir=export_path,
                            target="docx",
                        )
                        docx_run = run_process(docx_command, timeout_seconds=self.timeout_seconds)
                        if docx_run.timed_out:
                            return self._failure_result(
                                source=source,
                                output=output,
                                code="LIBREOFFICE_TIMEOUT",
                                title="LibreOffice timeout",
                                message=(
                                    "LibreOffice timed out after "
                                    f"{self.timeout_seconds} seconds."
                                ),
                                start=start,
                            )
                        if docx_run.returncode != 0:
                            stderr = docx_run.stderr.strip()
                            return self._failure_result(
                                source=source,
                                output=output,
                                code="LIBREOFFICE_DOCX_STAGE_FAILED",
                                title="DOC intermediate conversion failed",
                                message=stderr or "LibreOffice DOC -> DOCX conversion failed.",
                                start=start,
                            )
                        docx_output = _locate_exported_file(export_path, source, {".docx"})
                        if docx_output is None:
                            return self._failure_result(
                                source=source,
                                output=output,
                                code="LIBREOFFICE_DOCX_MISSING",
                                title="DOC intermediate missing",
                                message="LibreOffice did not produce DOCX intermediate output.",
                                start=start,
                            )
                        html_source = docx_output
                        warnings.append(
                            ConversionWarning(
                                code="DOC_INTERMEDIATE_DOCX",
                                message=(
                                    "Converted legacy .doc through .docx intermediate "
                                    "before markdown."
                                ),
                            )
                        )

                    html_command = _build_convert_command(
                        binary=binary,
                        profile_uri=profile_uri,
                        source=html_source,
                        outdir=export_path,
                        target="html",
                    )
                    html_run = run_process(html_command, timeout_seconds=self.timeout_seconds)
                    if html_run.timed_out:
                        return self._failure_result(
                            source=source,
                            output=output,
                            code="LIBREOFFICE_TIMEOUT",
                            title="LibreOffice timeout",
                            message=f"LibreOffice timed out after {self.timeout_seconds} seconds.",
                            start=start,
                        )
                    if html_run.returncode != 0:
                        stderr = html_run.stderr.strip()
                        return self._failure_result(
                            source=source,
                            output=output,
                            code="LIBREOFFICE_FAILED",
                            title="LibreOffice failed",
                            message=stderr or "LibreOffice returned a non-zero exit code.",
                            start=start,
                        )

                    html_output = _locate_exported_file(export_path, html_source, {".html", ".htm"})
                    if html_output is None:
                        return self._failure_result(
                            source=source,
                            output=output,
                            code="LIBREOFFICE_OUTPUT_MISSING",
                            title="Intermediate export missing",
                            message="LibreOffice completed but no HTML output was generated.",
                            start=start,
                        )
                    html = html_output.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            return self._failure_result(
                source=source,
                output=output,
                code="LIBREOFFICE_EXEC_ERROR",
                title="LibreOffice execution error",
                message=str(exc),
                start=start,
            )

        markdown, html_warnings = html_to_markdown(html)
        warnings.extend(html_warnings)
        if extension == ".odf":
            warnings.append(
                ConversionWarning(
                    code="ODF_CONVERSION_RISK",
                    message="ODF conversion may degrade formatting; review headings and tables.",
                )
            )
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
            metadata={
                "route": (
                    "libreoffice->docx->html->markdown"
                    if extension == ".doc"
                    else "libreoffice->html->markdown"
                )
            },
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


def _build_convert_command(
    *,
    binary: str,
    profile_uri: str,
    source: Path,
    outdir: Path,
    target: str,
) -> list[str]:
    return [
        binary,
        "--headless",
        "--nologo",
        "--nodefault",
        "--nolockcheck",
        "--norestore",
        f"-env:UserInstallation={profile_uri}",
        "--convert-to",
        target,
        "--outdir",
        str(outdir),
        str(source),
    ]


def _locate_exported_file(export_dir: Path, source: Path, suffixes: set[str]) -> Path | None:
    exact_candidates = [
        export_dir / f"{source.stem}{suffix}"
        for suffix in sorted(suffixes)
    ]
    for candidate in exact_candidates:
        if candidate.exists():
            return candidate

    lowered_stem = source.stem.lower()
    html_candidates = [
        item
        for item in export_dir.iterdir()
        if item.suffix.lower() in suffixes
    ]
    for candidate in html_candidates:
        if candidate.stem.lower() == lowered_stem:
            return candidate
    if html_candidates:
        return html_candidates[0]
    return None
