from __future__ import annotations

from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from app.core.settings import AppSettings
from app.search.service import KeywordSearchService, SearchFileResult


class SearchWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)
    progress = Signal(int, int, object)
    cancellation_requested = Signal()

    def __init__(
        self,
        input_files: list[str],
        query: str,
        settings: AppSettings,
        *,
        case_sensitive: bool = False,
    ) -> None:
        super().__init__()
        self._input_files = input_files
        self._query = query
        self._settings = settings
        self._case_sensitive = case_sensitive
        self._cancel_event = Event()

    @Slot()
    def run(self) -> None:
        try:
            service = KeywordSearchService(settings=self._settings)
            summary = service.search_files(
                [Path(item) for item in self._input_files],
                self._query,
                case_sensitive=self._case_sensitive,
                progress_callback=self._on_progress,
                should_cancel=self._should_cancel,
            )
            self.finished.emit(summary)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _on_progress(self, index: int, total: int, result: SearchFileResult) -> None:
        self.progress.emit(index, total, result)

    @Slot()
    def cancel(self) -> None:
        self._cancel_event.set()
        self.cancellation_requested.emit()

    def _should_cancel(self) -> bool:
        return self._cancel_event.is_set()
