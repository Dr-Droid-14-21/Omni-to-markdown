from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path


class FileStatus(StrEnum):
    PENDING = "pending"
    SCANNING = "scanning"
    READY = "ready"
    CONVERTING = "converting"
    CONVERTED = "converted"
    CONVERTED_WITH_WARNINGS = "converted_with_warnings"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(slots=True)
class ConversionWarning:
    code: str
    message: str
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.code.strip():
            msg = "warning code must not be empty"
            raise ValueError(msg)
        if not self.message.strip():
            msg = "warning message must not be empty"
            raise ValueError(msg)


@dataclass(slots=True)
class ConversionError:
    code: str
    severity: Severity
    title: str
    message: str
    technical_details: str = ""
    suggested_fix: str = ""
    retryable: bool = False

    def __post_init__(self) -> None:
        if not self.code.strip():
            msg = "error code must not be empty"
            raise ValueError(msg)
        if not self.title.strip():
            msg = "error title must not be empty"
            raise ValueError(msg)
        if not self.message.strip():
            msg = "error message must not be empty"
            raise ValueError(msg)


@dataclass(slots=True)
class ConversionPlan:
    source_path: Path
    output_path: Path
    detected_extension: str
    preferred_engine: str
    fallback_engines: list[str] = field(default_factory=list)
    warnings: list[ConversionWarning] = field(default_factory=list)
    requires_external_tools: bool = False
    estimated_risk_level: str = "low"

    def __post_init__(self) -> None:
        if not self.source_path.suffix:
            msg = "source_path must include an extension"
            raise ValueError(msg)
        if self.output_path.suffix.lower() != ".md":
            msg = "output_path must be a markdown file (.md)"
            raise ValueError(msg)
        if not self.detected_extension.startswith("."):
            msg = "detected_extension must start with '.'"
            raise ValueError(msg)
        if not self.preferred_engine.strip():
            msg = "preferred_engine must not be empty"
            raise ValueError(msg)


@dataclass(slots=True)
class ConversionResult:
    source_path: Path
    output_path: Path | None
    engine_name: str
    status: FileStatus
    warnings: list[ConversionWarning] = field(default_factory=list)
    errors: list[ConversionError] = field(default_factory=list)
    duration_ms: int = 0
    intermediate_files: list[Path] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class QueueItem:
    id: str
    source_path: Path
    display_name: str
    detected_type: str
    status: FileStatus = FileStatus.PENDING
    engine_route: str = ""
    output_path: Path | None = None
    warnings: list[ConversionWarning] = field(default_factory=list)
    errors: list[ConversionError] = field(default_factory=list)
    progress: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    result: ConversionResult | None = None

    def __post_init__(self) -> None:
        if not self.id.strip():
            msg = "queue item id must not be empty"
            raise ValueError(msg)
        if not self.display_name.strip():
            msg = "display_name must not be empty"
            raise ValueError(msg)
        if not 0.0 <= self.progress <= 100.0:
            msg = "progress must be between 0 and 100"
            raise ValueError(msg)


@dataclass(slots=True)
class StitchManifest:
    input_files: list[Path]
    output_path: Path
    normalize_line_endings: bool = True

    def __post_init__(self) -> None:
        if not self.input_files:
            msg = "stitch manifest must include at least one input file"
            raise ValueError(msg)
        if self.output_path.suffix.lower() != ".md":
            msg = "stitch output_path must be .md"
            raise ValueError(msg)


@dataclass(slots=True)
class StitchResult:
    output_path: Path
    file_count: int
    warnings: list[ConversionWarning] = field(default_factory=list)
