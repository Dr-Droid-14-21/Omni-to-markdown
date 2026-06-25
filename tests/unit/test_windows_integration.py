import re
from pathlib import Path

from app.core.file_detection import SUPPORTED_EXTENSIONS
from app.windows_integration import (
    SUPPORTED_CONTEXT_MENU_KEYS,
    ExplorerIntegrationStatus,
    context_menu_scripts,
    explorer_integration_status,
    launch_command_preview,
    packaged_executable_path,
    repo_root,
    run_context_menu_registration,
)


def test_explorer_integration_status_reports_missing_launcher(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.windows_integration.preferred_launch_target",
        lambda: None,
    )
    monkeypatch.setattr(
        "app.windows_integration.is_context_menu_installed",
        lambda: False,
    )
    monkeypatch.setattr(
        "app.windows_integration.is_sendto_shortcut_installed",
        lambda: False,
    )

    status = explorer_integration_status()

    assert status == ExplorerIntegrationStatus(
        available=False,
        installed=False,
        launch_target=None,
        detail="Build the Windows app or prepare .venv to enable Explorer integration.",
    )


def test_explorer_integration_status_reports_packaged_app_ready(monkeypatch) -> None:
    packaged_path = Path(r"C:\apps\OmniToMarkdown.exe")
    monkeypatch.setattr(
        "app.windows_integration.preferred_launch_target",
        lambda: packaged_path,
    )
    monkeypatch.setattr(
        "app.windows_integration.packaged_executable_path",
        lambda: packaged_path,
    )
    monkeypatch.setattr(
        "app.windows_integration.is_context_menu_installed",
        lambda: True,
    )
    monkeypatch.setattr(
        "app.windows_integration.is_sendto_shortcut_installed",
        lambda: True,
    )

    status = explorer_integration_status()

    assert status.available is True
    assert status.installed is True
    assert status.launch_target == packaged_path
    assert "Explorer menu and SendTo shortcut are installed" in status.detail


def test_context_menu_scripts_resolve_from_frozen_bundle(monkeypatch, tmp_path) -> None:
    bundle_root = tmp_path / "bundle"
    monkeypatch.setattr("sys.frozen", True, raising=False)
    monkeypatch.setattr("sys._MEIPASS", str(bundle_root), raising=False)

    register_script, unregister_script = context_menu_scripts()

    assert repo_root() == bundle_root
    assert register_script == bundle_root / "scripts" / "register_windows_context_menu.ps1"
    assert unregister_script == bundle_root / "scripts" / "unregister_windows_context_menu.ps1"


def test_packaged_executable_path_uses_frozen_executable(monkeypatch) -> None:
    frozen_exe = Path(r"C:\Program Files\OmniToMarkdown\OmniToMarkdown.exe")
    monkeypatch.setattr("sys.frozen", True, raising=False)
    monkeypatch.setattr("sys.executable", str(frozen_exe))

    assert packaged_executable_path() == frozen_exe


def test_frozen_context_menu_registration_passes_current_executable(
    monkeypatch,
    tmp_path,
) -> None:
    bundle_root = tmp_path / "bundle"
    frozen_exe = Path(r"C:\Program Files\OmniToMarkdown\OmniToMarkdown.exe")
    captured_command: list[str] = []

    monkeypatch.setattr("sys.frozen", True, raising=False)
    monkeypatch.setattr("sys._MEIPASS", str(bundle_root), raising=False)
    monkeypatch.setattr("sys.executable", str(frozen_exe))

    def fake_run_process(command: list[str], *, timeout_seconds: int) -> object:
        captured_command.extend(command)
        assert timeout_seconds == 20
        return object()

    monkeypatch.setattr("app.windows_integration.run_process", fake_run_process)

    run_context_menu_registration(install=True)

    assert "-ExecutablePath" in captured_command
    assert str(frozen_exe) in captured_command


def test_launch_command_preview_prefers_packaged_executable(monkeypatch) -> None:
    packaged_path = Path(r"C:\apps\OmniToMarkdown.exe")
    monkeypatch.setattr(
        "app.windows_integration.packaged_executable_path",
        lambda: packaged_path,
    )
    monkeypatch.setattr(
        "app.windows_integration.python_launcher_path",
        lambda: Path(r"C:\venv\Scripts\python.exe"),
    )
    monkeypatch.setattr(
        Path,
        "exists",
        lambda self: self == packaged_path,
    )

    preview = launch_command_preview()

    assert preview == f'"{packaged_path}" --convert-now "%1"'


def test_context_menu_keys_track_supported_conversion_extensions() -> None:
    expected_file_keys = {
        rf"Software\Classes\SystemFileAssociations\{extension}\shell\OmniToMarkdown"
        for extension in SUPPORTED_EXTENSIONS
    }
    actual_file_keys = {
        key for key in SUPPORTED_CONTEXT_MENU_KEYS if "SystemFileAssociations" in key
    }

    assert actual_file_keys == expected_file_keys
    assert r"Software\Classes\Directory\shell\OmniToMarkdown" in SUPPORTED_CONTEXT_MENU_KEYS


def test_context_menu_scripts_track_supported_conversion_extensions() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    check_script = repo_root / "scripts" / "check_windows_context_menu.ps1"
    register_script = repo_root / "scripts" / "register_windows_context_menu.ps1"
    unregister_script = repo_root / "scripts" / "unregister_windows_context_menu.ps1"
    scripts = [check_script, register_script, unregister_script]
    expected_extensions = set(SUPPORTED_EXTENSIONS)

    for script in scripts:
        content = script.read_text(encoding="utf-8")
        actual_extensions = set(
            re.findall(
                r"SystemFileAssociations\\(\.[a-z0-9]+)\\shell\\OmniToMarkdown",
                content,
            )
        )

        assert actual_extensions == expected_extensions
        assert r"Classes\Directory\shell\OmniToMarkdown" in content

    register_content = register_script.read_text(encoding="utf-8")
    unregister_content = unregister_script.read_text(encoding="utf-8")
    check_content = check_script.read_text(encoding="utf-8")
    assert "ExplorerMenuInstalled" in check_content
    assert "SendToShortcutInstalled" in check_content
    assert "ConvertTo-Json" in check_content
    assert "Omni to Markdown.lnk" in register_content
    assert "CreateShortcut" in register_content
    assert "Omni to Markdown.lnk" in unregister_content
    assert "Remove-Item" in unregister_content


def test_pyinstaller_spec_bundles_runtime_context_menu_scripts() -> None:
    repo_root_path = Path(__file__).resolve().parents[2]
    spec_content = (
        repo_root_path / "packaging" / "windows" / "OmniToMarkdown.spec"
    ).read_text(encoding="utf-8")

    assert "launch_omni.py" in spec_content
    assert "check_windows_context_menu.ps1" in spec_content
    assert "register_windows_context_menu.ps1" in spec_content
    assert "unregister_windows_context_menu.ps1" in spec_content
    assert 'datas.append((str(script_path), "scripts"))' in spec_content
