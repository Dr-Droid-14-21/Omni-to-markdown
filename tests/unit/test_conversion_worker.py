from pathlib import Path

from app.core.models import ConversionResult, FileStatus
from app.core.settings import AppSettings
from app.workers.conversion_worker import ConversionWorker


def _settings() -> AppSettings:
    return AppSettings.default()


def test_conversion_worker_emits_progress_and_finished(monkeypatch: object, tmp_path: Path) -> None:
    result = ConversionResult(
        source_path=Path("a.docx"),
        output_path=tmp_path / "a.md",
        engine_name="pandoc",
        status=FileStatus.CONVERTED,
    )

    class FakeService:
        def __init__(self, settings: AppSettings) -> None:
            self.settings = settings

        def convert_files(
            self,
            input_files: list[Path],
            output_dir: Path,
            progress_callback: object = None,
            should_cancel: object = None,
        ) -> list[ConversionResult]:
            if progress_callback is not None:
                progress_callback(1, 1, result)
            return [result]

    monkeypatch.setattr("app.workers.conversion_worker.ConversionService", FakeService)
    monkeypatch.setattr(
        "app.workers.conversion_worker.detect_engine_versions",
        lambda _: {"pandoc": "pandoc 3.0.0"},
    )

    progress_events: list[tuple[int, int, str]] = []
    finished_payload: dict[str, object] = {}
    failed_messages: list[str] = []

    worker = ConversionWorker(
        input_files=[str(tmp_path / "a.docx")],
        output_dir=str(tmp_path),
        settings=_settings(),
    )
    worker.progress.connect(
        lambda index, total, payload: progress_events.append(
            (index, total, payload.source_path.name)
        )
    )
    worker.finished.connect(
        lambda results, versions: finished_payload.update(
            {"results": results, "versions": versions}
        )
    )
    worker.failed.connect(lambda message: failed_messages.append(message))

    worker.run()

    assert failed_messages == []
    assert progress_events == [(1, 1, "a.docx")]
    assert len(finished_payload["results"]) == 1
    assert finished_payload["versions"] == {"pandoc": "pandoc 3.0.0"}


def test_conversion_worker_emits_failed_on_exception(monkeypatch: object, tmp_path: Path) -> None:
    class BrokenService:
        def __init__(self, settings: AppSettings) -> None:
            self.settings = settings

        def convert_files(
            self,
            input_files: list[Path],
            output_dir: Path,
            progress_callback: object = None,
            should_cancel: object = None,
        ) -> list[ConversionResult]:
            raise RuntimeError("boom")

    monkeypatch.setattr("app.workers.conversion_worker.ConversionService", BrokenService)

    failures: list[str] = []
    worker = ConversionWorker(
        input_files=[str(tmp_path / "a.docx")],
        output_dir=str(tmp_path),
        settings=_settings(),
    )
    worker.failed.connect(lambda message: failures.append(message))
    worker.run()

    assert failures == ["boom"]


def test_conversion_worker_cancel_flag_flows_to_service(
    monkeypatch: object,
    tmp_path: Path,
) -> None:
    seen_cancel_state: list[bool] = []

    class CancelAwareService:
        def __init__(self, settings: AppSettings) -> None:
            self.settings = settings

        def convert_files(
            self,
            input_files: list[Path],
            output_dir: Path,
            progress_callback: object = None,
            should_cancel: object = None,
        ) -> list[ConversionResult]:
            if callable(should_cancel):
                seen_cancel_state.append(bool(should_cancel()))
            return []

    monkeypatch.setattr("app.workers.conversion_worker.ConversionService", CancelAwareService)
    monkeypatch.setattr("app.workers.conversion_worker.detect_engine_versions", lambda _: {})

    worker = ConversionWorker(
        input_files=[str(tmp_path / "a.docx")],
        output_dir=str(tmp_path),
        settings=_settings(),
    )
    worker.cancel()
    worker.run()

    assert seen_cancel_state == [True]
