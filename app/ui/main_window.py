from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMessageBox, QStyle, QTabWidget

from app.ui.converter_tab import ConverterTab
from app.ui.neon_effects import NeonUiEffects
from app.ui.settings_dialog import SettingsDialog
from app.ui.stitcher_tab import StitcherTab


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("Omni to Markdown // Neon-GX")
        self.resize(1280, 820)
        self._init_ui()

    def _init_ui(self) -> None:
        tabs = QTabWidget(self)
        tabs.setObjectName("mainTabs")
        tabs.setDocumentMode(True)
        self.converter_tab = ConverterTab(self)
        tabs.addTab(self.converter_tab, "CONVERTER")
        tabs.addTab(StitcherTab(self), "MD STITCHER")
        self.setCentralWidget(tabs)
        self._build_menu()
        self.statusBar().showMessage("SYSTEM READY")
        self._ui_fx = NeonUiEffects(self)
        self._ui_fx.install()

    def _build_menu(self) -> None:
        menu = self.menuBar()
        style = self.style()

        file_menu = menu.addMenu("&File")
        settings_action = QAction("&Settings", self)
        settings_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        settings_action.triggered.connect(self._open_settings)
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menu.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About Omni to Markdown",
            "Omni to Markdown\nWindows-first document conversion and markdown stitching app.",
        )

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.converter_tab.reload_settings()
            self.statusBar().showMessage("Settings saved", 2500)
