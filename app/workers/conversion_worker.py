from __future__ import annotations

from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from app.conversion.dependency_check import detect_engine_versions
from app.conversion.service import ConversionService
from app.core.settings import AppSettings


class ConversionWorker(QObject):
    finished = Signal(object, object)
    failed = Signal(str)
    progress = Signal(int, int, object)
    cancellation_requested = Signal()

    def __init__(self, input_files: list[str], output_dir: str, settings: AppSettings) -> None:
        super().__init__()
        self._input_files = input_files
        self._output_dir = output_dir
        self._settings = settings
        self._cancel_event = Event()

    @Slot()
    def run(self) -> None:
        try:
            service = ConversionService(settings=self._settings)
            paths = [Path(item) for item in self._input_files]
            output_dir = Path(self._output_dir)
            results = service.convert_files(
                paths,
                output_dir,
                progress_callback=self._on_progress,
                should_cancel=self._should_cancel,
            )
            engine_versions = detect_engine_versions(self._settings)
            self.finished.emit(results, engine_versions)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _on_progress(self, index: int, total: int, result: object) -> None:
        self.progress.emit(index, total, result)

    @Slot()
    def cancel(self) -> None:
        self._cancel_event.set()
        self.cancellation_requested.emit()

    def _should_cancel(self) -> bool:
        return self._cancel_event.is_set()
