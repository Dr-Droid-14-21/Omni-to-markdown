import subprocess
from types import SimpleNamespace

from app.core.process import run_process, terminate_process_tree


def test_run_process_success(monkeypatch: object) -> None:
    class FakeProcess:
        pid = 100
        returncode = 0

        def communicate(self, timeout: int | None = None) -> tuple[str, str]:
            assert timeout == 5
            return ("ok", "")

    monkeypatch.setattr("subprocess.Popen", lambda *_args, **_kwargs: FakeProcess())
    result = run_process(["tool"], timeout_seconds=5)

    assert result.returncode == 0
    assert result.stdout == "ok"
    assert result.timed_out is False


def test_run_process_timeout_terminates_tree(monkeypatch: object) -> None:
    class FakeProcess:
        pid = 42
        returncode = -1

        def __init__(self) -> None:
            self.call_count = 0

        def communicate(self, timeout: int | None = None) -> tuple[str, str]:
            if self.call_count == 0:
                self.call_count += 1
                raise subprocess.TimeoutExpired(cmd=["tool"], timeout=timeout or 1)
            return ("", "late stderr")

    killed: list[int] = []

    monkeypatch.setattr("subprocess.Popen", lambda *_args, **_kwargs: FakeProcess())
    monkeypatch.setattr("app.core.process.terminate_process_tree", lambda pid: killed.append(pid))

    result = run_process(["tool"], timeout_seconds=1)

    assert result.timed_out is True
    assert result.stderr == "late stderr"
    assert killed == [42]


def test_terminate_process_tree_windows_uses_taskkill(monkeypatch: object) -> None:
    calls: list[list[str]] = []

    monkeypatch.setattr("app.core.process.os.name", "nt", raising=False)
    monkeypatch.setattr(
        "subprocess.run",
        lambda command, **_kwargs: calls.append(command) or SimpleNamespace(returncode=0),
    )

    terminate_process_tree(88)

    assert calls == [["taskkill", "/PID", "88", "/T", "/F"]]
