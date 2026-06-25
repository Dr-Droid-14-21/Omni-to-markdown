from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class LaunchOptions:
    selected_paths: list[Path] = field(default_factory=list)
    auto_convert: bool = False
    suppress_splash: bool = False
    self_check: bool = False


def parse_launch_options(argv: list[str]) -> LaunchOptions:
    options = LaunchOptions()

    for raw_arg in argv:
        arg = raw_arg.strip()
        if not arg:
            continue
        if arg == "--convert-now":
            options.auto_convert = True
            continue
        if arg == "--no-splash":
            options.suppress_splash = True
            continue
        if arg == "--self-check":
            options.self_check = True
            continue
        if arg.startswith("--"):
            continue
        options.selected_paths.append(Path(arg).expanduser())

    return options
