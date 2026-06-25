from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLabel, QMainWindow, QMessageBox, QStyle, QTabWidget

from app.release_readiness import inspect_release_readiness
from app.ui.converter_tab import ConverterTab
from app.ui.neon_effects import NeonUiEffects
from app.ui.release_readiness_dialog import ReleaseReadinessDialog
from app.ui.settings_dialog import SettingsDialog
from app.ui.stitcher_tab import StitcherTab
from app.windows_integration import explorer_integration_status, run_context_menu_registration


class MainWindow(QMainWindow):
    def __init__(
        self,
        initial_paths: list[Path] | None = None,
        auto_convert: bool = False,
    ) -> None:
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("Omni to Markdown // Neon-GX")
        self.resize(1280, 820)
        self._initial_paths = list(initial_paths or [])
        self._auto_convert = auto_convert
        self._init_ui()

    def _init_ui(self) -> None:
        tabs = QTabWidget(self)
        tabs.setObjectName("mainTabs")
        tabs.setDocumentMode(True)
        self.tabs = tabs
        self.converter_tab = ConverterTab(self)
        tabs.addTab(self.converter_tab, "CONVERTER")
        tabs.addTab(StitcherTab(self), "MD STITCHER")
        self.setCentralWidget(tabs)
        self._build_menu()
        self._build_status_bar()
        self._refresh_system_status("SYSTEM READY")
        self._ui_fx = NeonUiEffects(self)
        self._ui_fx.install()
        if self._initial_paths:
            self.converter_tab.import_launch_paths(
                self._initial_paths,
                auto_convert=self._auto_convert,
            )

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

        tools_menu = menu.addMenu("&Tools")
        install_explorer_action = QAction("&Install Explorer Menu", self)
        install_explorer_action.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        )
        install_explorer_action.triggered.connect(self._install_explorer_menu)
        tools_menu.addAction(install_explorer_action)

        remove_explorer_action = QAction("&Remove Explorer Menu", self)
        remove_explorer_action.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton)
        )
        remove_explorer_action.triggered.connect(self._remove_explorer_menu)
        tools_menu.addAction(remove_explorer_action)
        tools_menu.addSeparator()

        release_action = QAction("&Release Readiness", self)
        release_action.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)
        )
        release_action.triggered.connect(self._open_release_readiness)
        tools_menu.addAction(release_action)

        help_menu = menu.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _build_status_bar(self) -> None:
        self.workflow_status_label = QLabel("Workflow: ready")
        self.explorer_status_label = QLabel("Explorer: checking")
        self.package_status_label = QLabel("Package: checking")
        for label in (
            self.workflow_status_label,
            self.explorer_status_label,
            self.package_status_label,
        ):
            label.setObjectName("statusPill")
            self.statusBar().addPermanentWidget(label)

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About Omni to Markdown",
            "Omni to Markdown\n\n"
            "Windows-first document conversion, Markdown stitching, Explorer handoff, "
            "and local privacy-focused processing.",
        )

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.converter_tab.reload_settings()
            self._refresh_system_status("Settings saved")

    def _open_release_readiness(self) -> None:
        dialog = ReleaseReadinessDialog(self)
        dialog.exec()
        self._refresh_system_status("Release readiness checked")

    def _install_explorer_menu(self) -> None:
        result = run_context_menu_registration(install=True)
        self._handle_explorer_result(
            result=result,
            success_message="Explorer menu and SendTo shortcut installed.",
            failure_prefix="Failed to install Explorer integration",
        )

    def _remove_explorer_menu(self) -> None:
        result = run_context_menu_registration(install=False)
        self._handle_explorer_result(
            result=result,
            success_message="Explorer menu removed.",
            failure_prefix="Failed to remove Explorer menu",
        )

    def _handle_explorer_result(
        self,
        *,
        result: object,
        success_message: str,
        failure_prefix: str,
    ) -> None:
        returncode = getattr(result, "returncode", 1)
        timed_out = bool(getattr(result, "timed_out", False))
        stdout = str(getattr(result, "stdout", ""))
        stderr = str(getattr(result, "stderr", ""))
        if timed_out:
            QMessageBox.critical(self, "Explorer integration", f"{failure_prefix}: timed out.")
        elif returncode != 0:
            detail = stderr.strip() or stdout.strip() or "Unknown error."
            QMessageBox.critical(self, "Explorer integration", f"{failure_prefix}.\n\n{detail}")
        else:
            QMessageBox.information(self, "Explorer integration", success_message)
        self.converter_tab.reload_settings()
        self._refresh_system_status(success_message)

    def _refresh_system_status(self, message: str | None = None) -> None:
        explorer = explorer_integration_status()
        readiness = inspect_release_readiness()
        self.workflow_status_label.setText("Workflow: ready")
        explorer_complete = explorer.installed and explorer.sendto_installed
        self.explorer_status_label.setText(
            "Explorer: installed" if explorer_complete else "Explorer: incomplete"
        )
        self.package_status_label.setText(
            "Package: built" if readiness.packaged_app_exists else "Package: dev mode"
        )
        if message:
            self.statusBar().showMessage(message, 3000)

    def play_sound(self, name: str) -> None:
        self._ui_fx.play_sound(name)
