from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from app.core.file_detection import SUPPORTED_EXTENSIONS
from app.core.process import ProcessRunResult, run_process

if sys.platform == "win32":
    import winreg
else:  # pragma: no cover - non-Windows only.
    winreg = None  # type: ignore[assignment]


CONTEXT_MENU_REGISTRY_BASE = r"Software\Classes"
CONTEXT_MENU_VERB = "OmniToMarkdown"
SENDTO_SHORTCUT_NAME = "Omni to Markdown.lnk"
SUPPORTED_CONTEXT_MENU_KEYS = tuple(
    rf"{CONTEXT_MENU_REGISTRY_BASE}\SystemFileAssociations\{extension}\shell\{CONTEXT_MENU_VERB}"
    for extension in sorted(SUPPORTED_EXTENSIONS)
) + (
    rf"{CONTEXT_MENU_REGISTRY_BASE}\Directory\shell\{CONTEXT_MENU_VERB}",
)


@dataclass(slots=True)
class ExplorerIntegrationStatus:
    available: bool
    installed: bool
    launch_target: Path | None
    detail: str
    sendto_installed: bool = False


@dataclass(slots=True)
class ContextMenuCoverage:
    register_script_ok: bool
    unregister_script_ok: bool
    supported_extensions: tuple[str, ...]
    detail: str

    @property
    def ok(self) -> bool:
        return self.register_script_ok and self.unregister_script_ok


def repo_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS).resolve()  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[1]


def context_menu_scripts() -> tuple[Path, Path]:
    scripts_dir = repo_root() / "scripts"
    return (
        scripts_dir / "register_windows_context_menu.ps1",
        scripts_dir / "unregister_windows_context_menu.ps1",
    )


def packaged_executable_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    return repo_root() / "dist" / "OmniToMarkdown" / "OmniToMarkdown.exe"


def python_launcher_path() -> Path:
    return repo_root() / ".venv" / "Scripts" / "python.exe"


def launch_script_path() -> Path:
    return repo_root() / "scripts" / "launch_omni.py"


def sendto_shortcut_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "Microsoft" / "Windows" / "SendTo" / SENDTO_SHORTCUT_NAME
    return (
        Path.home()
        / "AppData"
        / "Roaming"
        / "Microsoft"
        / "Windows"
        / "SendTo"
        / SENDTO_SHORTCUT_NAME
    )


def preferred_launch_target() -> Path | None:
    packaged = packaged_executable_path()
    if packaged.exists():
        return packaged
    python_launcher = python_launcher_path()
    if python_launcher.exists():
        return python_launcher
    return None


def launch_command_preview() -> str:
    packaged = packaged_executable_path()
    if packaged.exists():
        return f'"{packaged}" --convert-now "%1"'
    python_launcher = python_launcher_path()
    return f'"{python_launcher}" "{launch_script_path()}" --convert-now "%1"'


def inspect_context_menu_script_coverage() -> ContextMenuCoverage:
    register_script, unregister_script = context_menu_scripts()
    supported = tuple(sorted(SUPPORTED_EXTENSIONS))
    register_ok, register_detail = _script_covers_supported_extensions(register_script, supported)
    unregister_ok, unregister_detail = _script_covers_supported_extensions(
        unregister_script,
        supported,
    )
    detail = (
        f"Register script: {register_detail} "
        f"Unregister script: {unregister_detail}"
    )
    return ContextMenuCoverage(
        register_script_ok=register_ok,
        unregister_script_ok=unregister_ok,
        supported_extensions=supported,
        detail=detail,
    )


def explorer_integration_status() -> ExplorerIntegrationStatus:
    target = preferred_launch_target()
    available = target is not None
    installed = is_context_menu_installed()
    sendto_installed = is_sendto_shortcut_installed()

    if not available:
        return ExplorerIntegrationStatus(
            available=False,
            installed=installed,
            launch_target=None,
            detail="Build the Windows app or prepare .venv to enable Explorer integration.",
            sendto_installed=sendto_installed,
        )

    target_label = "Packaged app" if target == packaged_executable_path() else "Python launcher"
    if installed and sendto_installed:
        detail = f"{target_label} ready. Explorer menu and SendTo shortcut are installed."
    elif installed:
        detail = f"{target_label} ready. Explorer menu is installed; SendTo shortcut is missing."
    elif sendto_installed:
        detail = f"{target_label} ready. SendTo shortcut is installed; Explorer menu is missing."
    else:
        detail = f"{target_label} ready. Explorer menu and SendTo shortcut are not installed yet."
    return ExplorerIntegrationStatus(
        available=True,
        installed=installed,
        launch_target=target,
        detail=detail,
        sendto_installed=sendto_installed,
    )


def is_context_menu_installed() -> bool:
    if sys.platform != "win32" or winreg is None:
        return False

    for key_path in SUPPORTED_CONTEXT_MENU_KEYS:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path):
                continue
        except FileNotFoundError:
            return False
    return True


def is_sendto_shortcut_installed() -> bool:
    if sys.platform != "win32":
        return False
    return sendto_shortcut_path().exists()


def run_context_menu_registration(*, install: bool) -> ProcessRunResult:
    register_script, unregister_script = context_menu_scripts()
    script_path = register_script if install else unregister_script
    command = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
    ]
    if install and getattr(sys, "frozen", False):
        command.extend(["-ExecutablePath", str(packaged_executable_path())])
    return run_process(command, timeout_seconds=20)


def _script_covers_supported_extensions(
    script_path: Path,
    supported_extensions: tuple[str, ...],
) -> tuple[bool, str]:
    if not script_path.exists():
        return False, f"{script_path.name} missing."

    content = script_path.read_text(encoding="utf-8")
    actual = set(
        re.findall(
            r"SystemFileAssociations\\(\.[a-z0-9]+)\\shell\\OmniToMarkdown",
            content,
        )
    )
    expected = set(supported_extensions)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    has_directory_key = r"Classes\Directory\shell\OmniToMarkdown" in content

    if missing or extra or not has_directory_key:
        issues: list[str] = []
        if missing:
            issues.append(f"missing {', '.join(missing)}")
        if extra:
            issues.append(f"unexpected {', '.join(extra)}")
        if not has_directory_key:
            issues.append("missing folder key")
        return False, f"{script_path.name} coverage mismatch ({'; '.join(issues)})."

    return True, f"{script_path.name} covers {', '.join(sorted(actual))} plus folders."
