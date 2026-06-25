from __future__ import annotations

from pathlib import Path

from app.core.models import ConversionPlan, ConversionWarning

SUPPORTED_EXTENSIONS = {
    ".doc",
    ".docx",
    ".htm",
    ".html",
    ".pdf",
    ".odt",
    ".odf",
    ".rtf",
    ".txt",
}


def build_plan(source_path: Path, output_path: Path) -> ConversionPlan:
    ext = source_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        msg = f"unsupported extension: {ext}"
        raise ValueError(msg)

    preferred_engine = _preferred_engine_for(ext)
    fallback = _fallback_engines_for(ext)
    warnings: list[ConversionWarning] = []

    if ext == ".pdf":
        warnings.append(
            ConversionWarning(
                code="PDF_LAYOUT_RISK",
                message="PDF conversion quality depends on source layout and text layer.",
            )
        )

    return ConversionPlan(
        source_path=source_path,
        output_path=output_path,
        detected_extension=ext,
        preferred_engine=preferred_engine,
        fallback_engines=fallback,
        warnings=warnings,
        requires_external_tools=ext in {".doc", ".docx", ".odt", ".odf", ".rtf"},
        estimated_risk_level=_risk_level_for(ext),
    )


def _preferred_engine_for(extension: str) -> str:
    match extension:
        case ".docx":
            return "pandoc"
        case ".odt":
            return "pandoc"
        case ".doc":
            return "libreoffice"
        case ".odf" | ".rtf":
            return "libreoffice"
        case ".htm" | ".html":
            return "html"
        case ".txt":
            return "text"
        case ".pdf":
            return "pymupdf"
        case _:
            return "unknown"


def _fallback_engines_for(extension: str) -> list[str]:
    match extension:
        case ".docx":
            return ["mammoth", "libreoffice"]
        case ".odt":
            return ["libreoffice"]
        case ".doc":
            return ["pandoc"]
        case ".odf":
            return ["text-fallback"]
        case ".htm" | ".html":
            return ["pandoc"]
        case ".pdf":
            return ["pdfminer"]
        case _:
            return []


def _risk_level_for(extension: str) -> str:
    return {
        ".docx": "low",
        ".htm": "low",
        ".html": "low",
        ".odt": "low",
        ".pdf": "medium",
        ".rtf": "medium",
        ".doc": "high",
        ".odf": "high",
        ".txt": "low",
    }.get(extension, "high")
