from __future__ import annotations

from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from app.core.models import StitchManifest, StitchResult
from app.stitcher.stitcher_service import StitchCancelledError, StitcherService


class StitchWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)
    cancelled = Signal(str)
    cancellation_requested = Signal()

    def __init__(self, input_files: list[str], output_file: str) -> None:
        super().__init__()
        self._input_files = input_files
        self._output_file = output_file
        self._cancel_event = Event()

    @Slot()
    def run(self) -> None:
        try:
            if self._cancel_event.is_set():
                self.cancelled.emit("Stitch cancelled before start.")
                return

            manifest = StitchManifest(
                input_files=[Path(item) for item in self._input_files],
                output_path=Path(self._output_file),
            )
            service = StitcherService()
            result: StitchResult = service.stitch(manifest, should_cancel=self._should_cancel)
            self.finished.emit(result)
        except StitchCancelledError as exc:
            self.cancelled.emit(str(exc))
        except Exception as exc:
            self.failed.emit(str(exc))

    @Slot()
    def cancel(self) -> None:
        self._cancel_event.set()
        self.cancellation_requested.emit()

    def _should_cancel(self) -> bool:
        return self._cancel_event.is_set()
