from __future__ import annotations

import os
import signal
import subprocess
from dataclasses import dataclass


@dataclass(slots=True)
class ProcessRunResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


def run_process(command: list[str], timeout_seconds: int) -> ProcessRunResult:
    popen_kwargs: dict[str, object] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        popen_kwargs["start_new_session"] = True

    process = subprocess.Popen(command, **popen_kwargs)
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        return ProcessRunResult(
            returncode=process.returncode or 0,
            stdout=stdout or "",
            stderr=stderr or "",
            timed_out=False,
        )
    except subprocess.TimeoutExpired:
        terminate_process_tree(process.pid)
        stdout, stderr = process.communicate()
        return ProcessRunResult(
            returncode=process.returncode if process.returncode is not None else -1,
            stdout=stdout or "",
            stderr=stderr or "",
            timed_out=True,
        )


def terminate_process_tree(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True,
            text=True,
            check=False,
        )
        return
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        return
