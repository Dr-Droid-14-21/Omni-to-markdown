from __future__ import annotations

import os
import stat
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from app.core.models import ConversionWarning

SUPPORTED_EXTENSIONS = {".doc", ".docx", ".pdf", ".odt", ".odf"}
PDF_MAGIC = b"%PDF-"
ZIP_MAGIC = b"PK"
OLE_MAGIC = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"


@dataclass(slots=True)
class FilePreflight:
    source_path: Path
    extension: str
    supported: bool
    warnings: list[ConversionWarning] = field(default_factory=list)
    error: str = ""
    detected_kind: str = "unknown"

    @property
    def can_queue(self) -> bool:
        return self.supported and not self.error


def detect_file(source_path: Path) -> FilePreflight:
    source = source_path.expanduser()
    extension = source.suffix.lower()
    preflight = FilePreflight(
        source_path=source,
        extension=extension,
        supported=extension in SUPPORTED_EXTENSIONS,
    )

    if not source.exists():
        preflight.error = "File does not exist."
        return preflight
    if not source.is_file():
        preflight.error = "Path is not a file."
        return preflight
    if not os.access(source, os.R_OK):
        preflight.error = "File is not readable."
        return preflight
    if not preflight.supported:
        preflight.error = f"Unsupported file extension: {extension or '(none)'}"
        return preflight

    _warn_if_windows_offline_placeholder(source, preflight)
    _header_checks(source, preflight)
    preflight.detected_kind = _kind_for_extension(extension)
    return preflight


def detect_many(paths: list[Path]) -> list[FilePreflight]:
    return [detect_file(path) for path in paths]


def check_output_directory_writable(output_dir: Path) -> tuple[bool, str]:
    target = output_dir.expanduser()
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return False, f"Unable to create output directory: {exc}"

    try:
        with tempfile.NamedTemporaryFile(dir=target, delete=True):
            pass
    except OSError as exc:
        return False, f"Output directory is not writable: {exc}"
    return True, ""


def _header_checks(source: Path, preflight: FilePreflight) -> None:
    header = _read_header(source)

    if preflight.extension == ".pdf":
        if not header.startswith(PDF_MAGIC):
            preflight.warnings.append(
                ConversionWarning(
                    code="HEADER_MISMATCH",
                    message="Extension is .pdf but file signature does not look like a PDF.",
                )
            )
    elif preflight.extension == ".doc":
        if not header.startswith(OLE_MAGIC):
            preflight.warnings.append(
                ConversionWarning(
                    code="HEADER_MISMATCH",
                    message="Extension is .doc but file signature does not look like legacy Word.",
                )
            )
    elif preflight.extension in {".docx", ".odt"}:
        if not header.startswith(ZIP_MAGIC):
            preflight.warnings.append(
                ConversionWarning(
                    code="HEADER_MISMATCH",
                    message=(
                        f"Extension is {preflight.extension} but file signature "
                        "is not ZIP-like."
                    ),
                )
            )
    elif preflight.extension == ".odf":
        preflight.warnings.append(
            ConversionWarning(
                code="ODF_AMBIGUOUS",
                message="ODF support is guarded and may require fallback conversion.",
            )
        )


def _read_header(source: Path, length: int = 16) -> bytes:
    with source.open("rb") as handle:
        return handle.read(length)


def _kind_for_extension(extension: str) -> str:
    return {
        ".doc": "word-legacy",
        ".docx": "word-openxml",
        ".pdf": "pdf",
        ".odt": "opendocument-text",
        ".odf": "opendocument-formula-or-generic",
    }.get(extension, "unknown")


def _warn_if_windows_offline_placeholder(source: Path, preflight: FilePreflight) -> None:
    if os.name != "nt":
        return

    try:
        attrs = os.stat(source).st_file_attributes
    except (AttributeError, OSError):
        return

    offline = getattr(stat, "FILE_ATTRIBUTE_OFFLINE", 0)
    recall_on_open = getattr(stat, "FILE_ATTRIBUTE_RECALL_ON_OPEN", 0)
    recall_on_data = getattr(stat, "FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS", 0)
    if attrs & (offline | recall_on_open | recall_on_data):
        preflight.warnings.append(
            ConversionWarning(
                code="CLOUD_PLACEHOLDER_POSSIBLE",
                message="File may be cloud-managed/offline and not fully available locally.",
            )
        )
