from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from app.conversion.libreoffice_engine import LibreOfficeEngine
from app.conversion.mammoth_engine import MammothEngine
from app.conversion.pandoc_engine import PandocEngine
from app.conversion.pdf_pdfminer_engine import PDFMinerEngine
from app.conversion.pdf_pymupdf_engine import PyMuPDFEngine
from app.conversion.router import build_plan
from app.core.models import (
    ConversionError,
    ConversionPlan,
    ConversionResult,
    ConversionWarning,
    FileStatus,
    Severity,
)
from app.core.settings import AppSettings, load_settings


class ConversionService:
    def __init__(self, settings: AppSettings | None = None) -> None:
        self.settings = settings or load_settings()
        self.pandoc_engine = PandocEngine(settings=self.settings)
        self.mammoth_engine = MammothEngine(settings=self.settings)
        self.libreoffice_engine = LibreOfficeEngine(settings=self.settings)
        self.pymupdf_engine = PyMuPDFEngine()
        self.pdfminer_engine = PDFMinerEngine()
        self._engines = {
            self.pandoc_engine.name: self.pandoc_engine,
            self.mammoth_engine.name: self.mammoth_engine,
            self.libreoffice_engine.name: self.libreoffice_engine,
            self.pymupdf_engine.name: self.pymupdf_engine,
            self.pdfminer_engine.name: self.pdfminer_engine,
        }

    def convert_files(
        self,
        input_files: list[Path],
        output_dir: Path,
        progress_callback: Callable[[int, int, ConversionResult], None] | None = None,
        should_cancel: Callable[[], bool] | None = None,
    ) -> list[ConversionResult]:
        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[ConversionResult] = []
        total = len(input_files)
        for index, source in enumerate(input_files, start=1):
            if should_cancel is not None and should_cancel():
                self._append_cancelled_results(
                    pending_sources=input_files[index - 1 :],
                    output_dir=output_dir,
                    results=results,
                    total=total,
                    progress_callback=progress_callback,
                )
                break

            output_path = self._resolve_output_path(output_dir, source.stem)
            plan = build_plan(source, output_path)
            result = self._convert_with_fallbacks(source, output_path, plan)

            results.append(result)
            if progress_callback is not None:
                progress_callback(index, total, result)
        return results

    def _convert_with_fallbacks(
        self,
        source: Path,
        output_path: Path,
        plan: ConversionPlan,
    ) -> ConversionResult:
        sequence = [plan.preferred_engine, *plan.fallback_engines]
        failed_results: list[ConversionResult] = []

        for step_index, engine_name in enumerate(sequence):
            engine = self._engines.get(engine_name)
            if engine is None:
                continue
            if not engine.can_convert(source, plan):
                continue

            result = engine.convert(source, output_path, plan)
            if result.status in {FileStatus.CONVERTED, FileStatus.CONVERTED_WITH_WARNINGS}:
                if step_index > 0:
                    result.warnings.append(
                        ConversionWarning(
                            code="FALLBACK_ENGINE_USED",
                            message=f"Converted with fallback engine `{engine_name}`.",
                            detail=f"Preferred route `{plan.preferred_engine}` was not used.",
                        )
                    )
                result.warnings = [*plan.warnings, *result.warnings]
                return result
            failed_results.append(result)

        if failed_results:
            final = failed_results[-1]
            final.warnings = [*plan.warnings, *final.warnings]
            return final

        return ConversionResult(
            source_path=source,
            output_path=output_path,
            engine_name=plan.preferred_engine,
            status=FileStatus.FAILED,
            warnings=plan.warnings,
            errors=[
                ConversionError(
                    code="ENGINE_NOT_AVAILABLE",
                    severity=Severity.ERROR,
                    title="No available engine route",
                    message=(
                        "No available conversion engine could run this file. "
                        "Check installed dependencies and route settings."
                    ),
                )
            ],
        )

    def _append_cancelled_results(
        self,
        *,
        pending_sources: list[Path],
        output_dir: Path,
        results: list[ConversionResult],
        total: int,
        progress_callback: Callable[[int, int, ConversionResult], None] | None,
    ) -> None:
        for source in pending_sources:
            output_path = self._resolve_output_path(output_dir, source.stem)
            plan = build_plan(source, output_path)
            result = ConversionResult(
                source_path=source,
                output_path=output_path,
                engine_name=plan.preferred_engine,
                status=FileStatus.CANCELLED,
                warnings=[
                    *plan.warnings,
                    ConversionWarning(
                        code="CANCELLED_BY_USER",
                        message="Cancelled by user request before processing started.",
                    ),
                ],
            )
            results.append(result)
            if progress_callback is not None:
                progress_callback(len(results), total, result)

    def _resolve_output_path(self, output_dir: Path, stem: str) -> Path:
        base = output_dir / f"{stem}.md"
        if not base.exists():
            return base

        counter = 1
        while True:
            candidate = output_dir / f"{stem} ({counter}).md"
            if not candidate.exists():
                return candidate
            counter += 1
