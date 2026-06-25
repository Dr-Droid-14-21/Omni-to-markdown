from app.main import main
from app.self_check import run_self_check


def test_run_self_check_reports_current_runtime_ready() -> None:
    result = run_self_check()

    assert result.ok is True
    assert result.app_dirs_ready is True
    assert result.resources_ready is True
    assert result.detail == "Self-check passed."


def test_main_self_check_returns_without_starting_gui() -> None:
    assert main(["--self-check"]) == 0
