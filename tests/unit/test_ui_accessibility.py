from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton

from app.ui.converter_tab import ConverterTab
from app.ui.main_window import MainWindow
from app.ui.settings_dialog import SettingsDialog
from app.ui.stitcher_tab import StitcherTab


def _app() -> QApplication:
    existing = QApplication.instance()
    if existing is not None:
        return existing
    return QApplication([])


def test_main_window_constructs_with_accessible_primary_surfaces() -> None:
    _app()
    window = MainWindow()

    assert window.converter_tab.queue_table.accessibleName() == "Conversion queue"
    assert window.converter_tab.warning_panel.accessibleName() == "Conversion warnings and errors"


def test_converter_and_stitcher_buttons_have_accessible_names_and_tooltips() -> None:
    _app()
    widgets = [ConverterTab(), StitcherTab()]

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


def test_settings_dialog_fields_have_accessible_names() -> None:
    _app()
    dialog = SettingsDialog()

    assert dialog.output_dir_edit.accessibleName() == "Default output directory"
    assert dialog.pandoc_path_edit.accessibleName() == "Pandoc executable path"
    assert dialog.libreoffice_path_edit.accessibleName() == "LibreOffice executable path"
    assert dialog.java_path_edit.accessibleName() == "Java executable path"
    assert dialog.tika_path_edit.accessibleName() == "Apache Tika app jar"
    assert dialog.save_button.accessibleName() == "Save settings"
