from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
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
from app.ui.neon_effects import NeonUiEffects


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
        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(12)

        self.output_dir_edit = QLineEdit()
        self.pandoc_path_edit = QLineEdit()
        self.libreoffice_path_edit = QLineEdit()
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
        self._apply_accessibility()
        self._ui_fx = NeonUiEffects(self)
        self._ui_fx.install()

    def _apply_accessibility(self) -> None:
        self.output_dir_edit.setAccessibleName("Default output directory")
        self.output_dir_edit.setToolTip("Default folder used for converted Markdown files.")
        self.pandoc_path_edit.setAccessibleName("Pandoc executable path")
        self.pandoc_path_edit.setToolTip("Optional path override for the Pandoc executable.")
        self.libreoffice_path_edit.setAccessibleName("LibreOffice executable path")
        self.libreoffice_path_edit.setToolTip("Optional path override for soffice or LibreOffice.")
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
            max_file_size_warning_mb=self._settings.max_file_size_warning_mb,
            concurrency_limit=self.concurrency_spin.value(),
            privacy_mode=self.privacy_mode_check.isChecked(),
        )
        save_settings(settings)
        self.accept()
