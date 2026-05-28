from pathlib import Path

from app.core.models import StitchResult
from app.workers.stitch_worker import StitchWorker


def test_stitch_worker_emits_finished(monkeypatch: object, tmp_path: Path) -> None:
    output = tmp_path / "out.md"
    result = StitchResult(output_path=output, file_count=2)

    class FakeService:
        def stitch(self, manifest: object, should_cancel: object = None) -> StitchResult:
            assert callable(should_cancel)
            return result

    monkeypatch.setattr("app.workers.stitch_worker.StitcherService", FakeService)

    worker = StitchWorker(
        input_files=[str(tmp_path / "a.md"), str(tmp_path / "b.md")],
        output_file=str(output),
    )

    finished_results: list[StitchResult] = []
    failed_messages: list[str] = []
    cancelled_messages: list[str] = []
    worker.finished.connect(lambda payload: finished_results.append(payload))
    worker.failed.connect(lambda message: failed_messages.append(message))
    worker.cancelled.connect(lambda message: cancelled_messages.append(message))

    worker.run()

    assert len(finished_results) == 1
    assert failed_messages == []
    assert cancelled_messages == []


def test_stitch_worker_emits_cancelled_when_cancelled_before_run(tmp_path: Path) -> None:
    worker = StitchWorker(
        input_files=[str(tmp_path / "a.md")],
        output_file=str(tmp_path / "out.md"),
    )
    cancelled_messages: list[str] = []
    worker.cancelled.connect(lambda message: cancelled_messages.append(message))

    worker.cancel()
    worker.run()

    assert cancelled_messages == ["Stitch cancelled before start."]


def test_stitch_worker_emits_failed_on_exception(monkeypatch: object, tmp_path: Path) -> None:
    class BrokenService:
        def stitch(self, manifest: object, should_cancel: object = None) -> StitchResult:
            raise RuntimeError("boom")

    monkeypatch.setattr("app.workers.stitch_worker.StitcherService", BrokenService)
    worker = StitchWorker(
        input_files=[str(tmp_path / "a.md")],
        output_file=str(tmp_path / "out.md"),
    )
    failures: list[str] = []
    worker.failed.connect(lambda message: failures.append(message))

    worker.run()

    assert failures == ["boom"]
