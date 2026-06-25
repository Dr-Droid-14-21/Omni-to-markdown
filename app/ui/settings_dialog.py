from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from app.core.settings import AppSettings, load_settings, save_settings
from app.ui.button_metrics import apply_button_metrics_to
from app.ui.neon_effects import NeonUiEffects
from app.windows_integration import (
    explorer_integration_status,
    run_context_menu_registration,
)


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(680, 360)
        self._settings = load_settings()
        self._setup_ui()
        self._load_values()

    def _setup_ui(self) -> None:
        self.setObjectName("settingsDialog")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 22)
        root.setSpacing(14)
        root.addWidget(self._build_overview_panel())
        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(12)

        self.output_dir_edit = QLineEdit()
        self.pandoc_path_edit = QLineEdit()
        self.libreoffice_path_edit = QLineEdit()
        self.java_path_edit = QLineEdit()
        self.tika_path_edit = QLineEdit()
        self.markdown_flavor_edit = QLineEdit()
        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 8)
        self.privacy_mode_check = QCheckBox("Enable privacy mode")

        form.addRow(
            "Default output directory",
            self._with_browse(self.output_dir_edit, self._pick_folder),
        )
        form.addRow(
            "Pandoc executable path",
            self._with_browse(self.pandoc_path_edit, self._pick_file_for_pandoc),
        )
        form.addRow(
            "LibreOffice executable path",
            self._with_browse(self.libreoffice_path_edit, self._pick_file_for_libreoffice),
        )
        form.addRow(
            "Java executable path",
            self._with_browse(self.java_path_edit, self._pick_file_for_java),
        )
        form.addRow(
            "Apache Tika app jar",
            self._with_browse(self.tika_path_edit, self._pick_file_for_tika),
        )
        form.addRow("Markdown flavor", self.markdown_flavor_edit)
        form.addRow("Concurrency limit", self.concurrency_spin)
        form.addRow(QLabel(""), self.privacy_mode_check)

        root.addLayout(form)

        actions = QHBoxLayout()
        actions.addStretch()
        self.cancel_button = QPushButton("Cancel")
        self.save_button = QPushButton("Save")
        style = self.style()
        self.cancel_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
        self.save_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.cancel_button.setProperty("uiRole", "quiet")
        self.save_button.setProperty("uiRole", "primary")
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.save_button)
        root.addLayout(actions)

        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self._on_save)
        self.install_explorer_button.clicked.connect(self._on_install_explorer_menu)
        self.remove_explorer_button.clicked.connect(self._on_remove_explorer_menu)
        apply_button_metrics_to(self)
        self._apply_accessibility()
        self._ui_fx = NeonUiEffects(self)
        self._ui_fx.install()
        self._refresh_explorer_status()

    def _build_overview_panel(self) -> QWidget:
        card = QFrame(self)
        card.setObjectName("heroPanel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("System paths, engine overrides, and Windows integration.")
        title.setObjectName("heroTitle")
        layout.addWidget(title)

        copy = QLabel(
            "Use this panel to keep the desktop build dependable: set conversion engine "
            "paths, tune defaults, and control the Explorer right-click workflow from one place."
        )
        copy.setObjectName("heroCopy")
        copy.setWordWrap(True)
        layout.addWidget(copy)

        actions = QHBoxLayout()
        actions.setSpacing(12)
        style = self.style()
        self.install_explorer_button = QPushButton("Install Explorer Menu")
        self.install_explorer_button.setProperty("uiRole", "secondary")
        self.install_explorer_button.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        )
        self.remove_explorer_button = QPushButton("Remove Explorer Menu")
        self.remove_explorer_button.setProperty("uiRole", "quiet")
        self.remove_explorer_button.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton)
        )
        actions.addWidget(self.install_explorer_button)
        actions.addWidget(self.remove_explorer_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.explorer_status_label = QLabel("")
        self.explorer_status_label.setObjectName("heroCopy")
        self.explorer_status_label.setWordWrap(True)
        layout.addWidget(self.explorer_status_label)
        return card

    def _apply_accessibility(self) -> None:
        self.output_dir_edit.setAccessibleName("Default output directory")
        self.output_dir_edit.setToolTip("Default folder used for converted Markdown files.")
        self.pandoc_path_edit.setAccessibleName("Pandoc executable path")
        self.pandoc_path_edit.setToolTip("Optional path override for the Pandoc executable.")
        self.libreoffice_path_edit.setAccessibleName("LibreOffice executable path")
        self.libreoffice_path_edit.setToolTip("Optional path override for soffice or LibreOffice.")
        self.java_path_edit.setAccessibleName("Java executable path")
        self.java_path_edit.setToolTip(
            "Optional path override for the Java executable used by Tika."
        )
        self.tika_path_edit.setAccessibleName("Apache Tika app jar")
        self.tika_path_edit.setToolTip("Optional path override for tika-app-3.2.3.jar.")
        self.markdown_flavor_edit.setAccessibleName("Markdown flavor")
        self.markdown_flavor_edit.setToolTip(
            "Markdown flavor passed to supporting conversion engines."
        )
        self.concurrency_spin.setAccessibleName("Concurrency limit")
        self.concurrency_spin.setToolTip("Maximum number of conversion jobs allowed by settings.")
        self.privacy_mode_check.setAccessibleName("Privacy mode")
        self.privacy_mode_check.setToolTip("Keep reports and logs free of document body text.")
        self.cancel_button.setAccessibleName("Cancel settings")
        self.save_button.setAccessibleName("Save settings")
        self.install_explorer_button.setAccessibleName("Install Windows Explorer menu")
        self.install_explorer_button.setToolTip(
            "Install a user-level right-click entry for supported files and folders."
        )
        self.remove_explorer_button.setAccessibleName("Remove Windows Explorer menu")
        self.remove_explorer_button.setToolTip(
            "Remove the Omni to Markdown right-click entry from Explorer."
        )

    def _with_browse(self, edit: QLineEdit, handler: Callable[[], None]) -> QWidget:
        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        browse = QPushButton("Browse")
        browse.setProperty("uiRole", "secondary")
        browse.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        browse.setAccessibleName("Browse setting path")
        browse.setToolTip("Open a file or folder picker for this setting.")
        browse.clicked.connect(handler)
        layout.addWidget(edit)
        layout.addWidget(browse)
        return container

    def _load_values(self) -> None:
        settings = self._settings
        self.output_dir_edit.setText(settings.default_output_directory)
        self.pandoc_path_edit.setText(settings.pandoc_binary_path)
        self.libreoffice_path_edit.setText(settings.libreoffice_binary_path)
        self.java_path_edit.setText(settings.java_binary_path)
        self.tika_path_edit.setText(settings.tika_app_path)
        self.markdown_flavor_edit.setText(settings.markdown_flavor)
        self.concurrency_spin.setValue(settings.concurrency_limit)
        self.privacy_mode_check.setChecked(settings.privacy_mode)

    def _pick_folder(self) -> None:
        picked = QFileDialog.getExistingDirectory(self, "Select directory")
        if picked:
            self.output_dir_edit.setText(picked)

    def _pick_file_for_pandoc(self) -> None:
        picked, _ = QFileDialog.getOpenFileName(self, "Select pandoc executable")
        if picked:
            self.pandoc_path_edit.setText(picked)

    def _pick_file_for_libreoffice(self) -> None:
        picked, _ = QFileDialog.getOpenFileName(self, "Select LibreOffice executable")
        if picked:
            self.libreoffice_path_edit.setText(picked)

    def _pick_file_for_java(self) -> None:
        picked, _ = QFileDialog.getOpenFileName(self, "Select Java executable")
        if picked:
            self.java_path_edit.setText(picked)

    def _pick_file_for_tika(self) -> None:
        picked, _ = QFileDialog.getOpenFileName(
            self,
            "Select Apache Tika app jar",
            "",
            "Java Archives (*.jar);;All files (*.*)",
        )
        if picked:
            self.tika_path_edit.setText(picked)

    def _on_save(self) -> None:
        output_dir = self.output_dir_edit.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "Settings", "Default output directory is required.")
            return
        if not Path(output_dir).exists():
            try:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                QMessageBox.critical(self, "Settings", f"Unable to create output directory: {exc}")
                return

        settings = AppSettings(
            default_output_directory=output_dir,
            markdown_flavor=self.markdown_flavor_edit.text().strip() or "gfm",
            docx_engine_preference=self._settings.docx_engine_preference,
            pdf_extraction_mode=self._settings.pdf_extraction_mode,
            image_extraction_enabled=self._settings.image_extraction_enabled,
            table_handling=self._settings.table_handling,
            pandoc_binary_path=self.pandoc_path_edit.text().strip(),
            libreoffice_binary_path=self.libreoffice_path_edit.text().strip(),
            java_binary_path=self.java_path_edit.text().strip(),
            tika_app_path=self.tika_path_edit.text().strip(),
            max_file_size_warning_mb=self._settings.max_file_size_warning_mb,
            concurrency_limit=self.concurrency_spin.value(),
            privacy_mode=self.privacy_mode_check.isChecked(),
        )
        save_settings(settings)
        self.accept()

    def _on_install_explorer_menu(self) -> None:
        result = run_context_menu_registration(install=True)
        self._handle_explorer_result(
            action="install",
            success_message="Explorer menu and SendTo shortcut installed.",
            result=result,
        )

    def _on_remove_explorer_menu(self) -> None:
        result = run_context_menu_registration(install=False)
        self._handle_explorer_result(
            action="remove",
            success_message="Explorer integration removed.",
            result=result,
        )

    def _refresh_explorer_status(self) -> None:
        status = explorer_integration_status()
        explorer_complete = status.installed and status.sendto_installed
        self.explorer_status_label.setText(status.detail)
        self.install_explorer_button.setEnabled(status.available and not explorer_complete)
        self.remove_explorer_button.setEnabled(status.installed or status.sendto_installed)

    def _handle_explorer_result(
        self,
        *,
        action: str,
        success_message: str,
        result: object,
    ) -> None:
        returncode = getattr(result, "returncode", 1)
        timed_out = bool(getattr(result, "timed_out", False))
        stdout = str(getattr(result, "stdout", ""))
        stderr = str(getattr(result, "stderr", ""))

        if timed_out:
            QMessageBox.critical(self, "Explorer integration", f"{action.title()} timed out.")
        elif returncode != 0:
            detail = stderr.strip() or stdout.strip() or "Unknown error."
            QMessageBox.critical(
                self,
                "Explorer integration",
                f"Failed to {action} Explorer integration.\n\n{detail}",
            )
        else:
            QMessageBox.information(self, "Explorer integration", success_message)
        self._refresh_explorer_status()
