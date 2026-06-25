from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton

from app.conversion.dependency_check import DependencyStatus
from app.core.settings import AppSettings
from app.ui.converter_tab import ConverterTab
from app.ui.main_window import MainWindow
from app.ui.release_readiness_dialog import ReleaseReadinessDialog
from app.ui.settings_dialog import SettingsDialog
from app.ui.stitcher_tab import StitcherTab
from app.windows_integration import ExplorerIntegrationStatus


def _app() -> QApplication:
    existing = QApplication.instance()
    if existing is not None:
        return existing
    return QApplication([])


def test_main_window_constructs_with_accessible_primary_surfaces() -> None:
    _app()
    window = MainWindow()

    try:
        assert window.converter_tab.queue_table.accessibleName() == "Conversion queue"
        assert (
            window.converter_tab.warning_panel.accessibleName()
            == "Conversion warnings and errors"
        )
        assert "Drop documents or folders here" in (
            window.converter_tab.queue_table.accessibleDescription()
        )
        assert ".docx" in window.converter_tab.queue_table.empty_state_text()
        assert ".rtf" in window.converter_tab.queue_table.empty_state_text()
        assert ".txt" in window.converter_tab.queue_table.empty_state_text()
        assert window.explorer_status_label.text().startswith("Explorer:")
        assert window.package_status_label.text().startswith("Package:")
    finally:
        window.close()


def test_queue_drop_zone_copy_includes_all_supported_formats() -> None:
    _app()
    widget = ConverterTab()

    try:
        empty_text = widget.queue_table.empty_state_text()
        assert ".htm" in empty_text
        assert ".html" in empty_text

        widget.queue_table._set_drag_active(True)
        assert "Release to queue" in widget.queue_table.empty_state_text()
        assert "preserve sources" in widget.queue_table.empty_state_text()

        widget.queue_table._set_drag_active(False)
        assert "Drop documents or folders here" in widget.queue_table.empty_state_text()
    finally:
        widget.close()


def test_main_window_imports_initial_supported_paths_into_queue() -> None:
    _app()
    sample_pdf = Path("tests/fixtures/sample.pdf").resolve()

    window = MainWindow(initial_paths=[sample_pdf])

    try:
        assert window.converter_tab.queue_table.rowCount() == 1
        assert window.converter_tab.queue_table.queued_paths() == [str(sample_pdf)]
    finally:
        window.close()


def test_main_window_marks_explorer_incomplete_without_sendto(monkeypatch) -> None:
    _app()
    monkeypatch.setattr(
        "app.ui.main_window.explorer_integration_status",
        lambda: ExplorerIntegrationStatus(
            available=True,
            installed=True,
            sendto_installed=False,
            launch_target=Path(r"C:\apps\OmniToMarkdown.exe"),
            detail="Explorer menu is installed; SendTo shortcut is missing.",
        ),
    )

    window = MainWindow()

    try:
        assert window.explorer_status_label.text() == "Explorer: incomplete"
    finally:
        window.close()


def test_auto_convert_launch_suppresses_success_preflight_dialog(monkeypatch) -> None:
    _app()
    sample_pdf = Path("tests/fixtures/sample.pdf").resolve()
    output_dir = Path.cwd()
    convert_calls: list[int] = []

    def fake_dependencies(_: AppSettings) -> dict[str, DependencyStatus]:
        return {
            name: DependencyStatus(name=name, available=True, path=name)
            for name in (
                "pandoc",
                "libreoffice",
                "java",
                "tika",
                "mammoth",
                "pymupdf",
                "pdfminer",
            )
        }

    def fake_information(_: object, title: str, message: str) -> None:
        if title == "Preflight" and "passed" in message:
            raise AssertionError("Auto-convert launch should not show preflight success.")

    monkeypatch.setattr(
        "app.ui.converter_tab.load_settings",
        lambda: AppSettings(default_output_directory=str(output_dir)),
    )
    monkeypatch.setattr("app.ui.converter_tab.detect_all_dependencies", fake_dependencies)
    monkeypatch.setattr(QMessageBox, "information", fake_information)
    monkeypatch.setattr(
        ConverterTab,
        "_on_convert",
        lambda self: convert_calls.append(self.queue_table.rowCount()),
    )

    window = MainWindow(initial_paths=[sample_pdf], auto_convert=True)

    try:
        assert window.converter_tab.queue_table.rowCount() == 1
        assert convert_calls == [1]
    finally:
        window.close()


def test_converter_and_stitcher_buttons_have_accessible_names_and_tooltips() -> None:
    _app()
    widgets = [ConverterTab(), StitcherTab()]

    try:
        buttons = [
            button
            for widget in widgets
            for button in widget.findChildren(QPushButton)
            if button.text()
        ]

        assert buttons
        for button in buttons:
            assert button.accessibleName()
            assert button.toolTip()
            assert button.minimumHeight() >= 40
            assert button.iconSize().width() >= 20
            assert button.iconSize().height() >= 20
    finally:
        for widget in widgets:
            widget.close()


def test_settings_dialog_fields_have_accessible_names() -> None:
    _app()
    dialog = SettingsDialog()

    try:
        assert dialog.output_dir_edit.accessibleName() == "Default output directory"
        assert dialog.pandoc_path_edit.accessibleName() == "Pandoc executable path"
        assert dialog.libreoffice_path_edit.accessibleName() == "LibreOffice executable path"
        assert dialog.java_path_edit.accessibleName() == "Java executable path"
        assert dialog.tika_path_edit.accessibleName() == "Apache Tika app jar"
        assert dialog.save_button.accessibleName() == "Save settings"
        assert dialog.install_explorer_button.accessibleName() == "Install Windows Explorer menu"
        assert dialog.remove_explorer_button.accessibleName() == "Remove Windows Explorer menu"
    finally:
        dialog.close()


def test_settings_allows_reinstall_when_sendto_is_missing(monkeypatch) -> None:
    _app()
    monkeypatch.setattr(
        "app.ui.settings_dialog.explorer_integration_status",
        lambda: ExplorerIntegrationStatus(
            available=True,
            installed=True,
            sendto_installed=False,
            launch_target=Path(r"C:\apps\OmniToMarkdown.exe"),
            detail="Explorer menu is installed; SendTo shortcut is missing.",
        ),
    )

    dialog = SettingsDialog()

    try:
        assert dialog.install_explorer_button.isEnabled()
        assert dialog.remove_explorer_button.isEnabled()
        assert "SendTo shortcut is missing" in dialog.explorer_status_label.text()
    finally:
        dialog.close()


def test_release_readiness_dialog_shows_format_coverage() -> None:
    _app()
    dialog = ReleaseReadinessDialog()

    try:
        details = dialog.details_edit.toPlainText()
        assert "SendTo shortcut:" in details
        assert "Explorer format coverage:" in details
        assert "Supported input formats:" in details
        assert "Signature detail" in details
        assert ".txt" in details
    finally:
        dialog.close()


def test_stitcher_overview_updates_for_added_paths() -> None:
    _app()
    widget = StitcherTab()
    sample_markdown = Path("README.md").resolve()

    try:
        widget._add_paths([sample_markdown])

        assert widget.stitch_count_value.text() == "1"
        assert widget.stitch_mode_value.text() == "Tray Ready"
        assert widget.duplicate_count_value.text() == "0"
    finally:
        widget.close()
