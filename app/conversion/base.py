from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.core.models import ConversionPlan, ConversionResult


@dataclass(slots=True)
class EngineAvailability:
    available: bool
    reason: str = ""


class ConversionEngine(Protocol):
    name: str
    supported_extensions: set[str]

    def is_available(self) -> EngineAvailability:
        ...

    def can_convert(self, source: Path, plan: ConversionPlan) -> bool:
        ...

    def convert(self, source: Path, output: Path, plan: ConversionPlan) -> ConversionResult:
        ...
