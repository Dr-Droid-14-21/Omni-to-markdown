from __future__ import annotations

import time
from importlib import import_module
from pathlib import Path
from types import ModuleType

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


class PyMuPDFEngine(ConversionEngine):
    name = "pymupdf"
    supported_extensions = {".pdf"}

    def is_available(self) -> EngineAvailability:
        if _load_pymupdf_module() is None:
            return EngineAvailability(
                available=False,
                reason="Python package `pymupdf` is not installed.",
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
                title="PyMuPDF route unsupported",
                message=f"PyMuPDF engine does not support {source.suffix.lower()}.",
                start=start,
                engine_name=self.name,
            )

        fitz = _load_pymupdf_module()
        if fitz is None:
            return _failure_result(
                source=source,
                output=output,
                code="PYMUPDF_NOT_FOUND",
                title="PyMuPDF not available",
                message="Install `pymupdf` to enable PDF extraction.",
                start=start,
                engine_name=self.name,
            )

        try:
            document = fitz.open(str(source))
        except Exception as exc:  # noqa: BLE001
            message = str(exc)
            code = (
                "PDF_PASSWORD_PROTECTED"
                if _looks_like_password_error(message)
                else "PDF_OPEN_FAILED"
            )
            title = (
                "Password-protected PDF"
                if code == "PDF_PASSWORD_PROTECTED"
                else "PDF open failed"
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
        try:
            needs_pass = bool(getattr(document, "needs_pass", False))
            if needs_pass:
                return _failure_result(
                    source=source,
                    output=output,
                    code="PDF_PASSWORD_PROTECTED",
                    title="Password-protected PDF",
                    message="This PDF requires a password and cannot be processed automatically.",
                    start=start,
                    engine_name=self.name,
                )

            page_texts: list[str] = []
            image_heavy_pages: list[str] = []
            page_count = len(document)

            for page_index, page in enumerate(document, start=1):
                text = str(page.get_text("text") or "")
                normalized = text.strip()
                page_texts.append(normalized)
                has_images = len(page.get_images(full=True)) > 0
                if not normalized and has_images:
                    image_heavy_pages.append(str(page_index))

            non_empty_pages = [value for value in page_texts if value]
            if not non_empty_pages:
                warnings.append(
                    ConversionWarning(
                        code="PDF_NO_TEXT_LAYER",
                        message=(
                            "No extractable text layer was found in this PDF. "
                            "The file may be scanned images."
                        ),
                    )
                )
                markdown_body = ""
            else:
                markdown_body = "\n\n".join(non_empty_pages)

            if image_heavy_pages:
                warnings.append(
                    ConversionWarning(
                        code="PDF_IMAGE_HEAVY_PAGES",
                        message="Some pages appear image-heavy and may need OCR for full fidelity.",
                        detail=f"pages={','.join(image_heavy_pages)}",
                    )
                )
        finally:
            document.close()

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(normalize_markdown_text(markdown_body), encoding="utf-8", newline="\n")

        status = FileStatus.CONVERTED_WITH_WARNINGS if warnings else FileStatus.CONVERTED
        return ConversionResult(
            source_path=source,
            output_path=output,
            engine_name=self.name,
            status=status,
            warnings=warnings,
            duration_ms=int((time.monotonic() - start) * 1000),
            metadata={
                "page_count": str(page_count),
                "character_count": str(len(markdown_body)),
            },
        )


def _load_pymupdf_module() -> ModuleType | None:
    try:
        return import_module("fitz")
    except ImportError:
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
