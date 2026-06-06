from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from app.core.models import StitchManifest, StitchResult
from app.core.settings import load_settings
from app.search import format_search_summary
from app.stitcher.separator import build_separator
from app.stitcher.stitcher_service import StitcherValidationError
from app.stitcher.tray_manifest import StitchTrayError, load_stitch_tray, save_stitch_tray
from app.ui.button_metrics import apply_button_metrics_to
from app.ui.widgets.drag_drop_list import DragDropList
from app.ui.widgets.warning_panel import WarningPanel
from app.workers.search_worker import SearchWorker
from app.workers.stitch_worker import StitchWorker

TRAY_FILE_FILTER = "Omni Stitch Tray (*.omni-tray.json);;JSON Files (*.json)"
TRAY_FILE_SUFFIX = ".omni-tray.json"


class StitcherTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._is_stitching = False
        self._cancel_requested = False
        self._active_thread: QThread | None = None
        self._active_worker: StitchWorker | None = None
        self._is_searching = False
        self._active_search_thread: QThread | None = None
        self._active_search_worker: SearchWorker | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("stitcherTab")
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title = QLabel("OMNI STITCHER // MARKDOWN ASSEMBLY BAY")
        title.setObjectName("tabTitle")
        root.addWidget(title)
        subtitle = QLabel(
            "Order Markdown files, preview separators, then build one final document."
        )
        subtitle.setObjectName("tabSubtitle")
        root.addWidget(subtitle)

        controls = QGridLayout()
        controls.setHorizontalSpacing(10)
        controls.setVerticalSpacing(10)
        self.add_files_button = QPushButton("Add Files")
        self.load_tray_button = QPushButton("Load Tray")
        self.save_tray_button = QPushButton("Save Tray")
        self.remove_selected_button = QPushButton("Remove Selected")
        self.clear_button = QPushButton("Clear")
        self.move_up_button = QPushButton("Move Up")
        self.move_down_button = QPushButton("Move Down")
        self.add_files_button.setProperty("uiRole", "hero")
        self.load_tray_button.setProperty("uiRole", "secondary")
        self.save_tray_button.setProperty("uiRole", "secondary")
        self.remove_selected_button.setProperty("uiRole", "secondary")
        self.clear_button.setProperty("uiRole", "quiet")
        self.move_up_button.setProperty("uiRole", "secondary")
        self.move_down_button.setProperty("uiRole", "secondary")
        style = self.style()
        self.add_files_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.load_tray_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.save_tray_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.remove_selected_button.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        )
        self.clear_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        self.move_up_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        self.move_down_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_ArrowDown))

        controls.addWidget(self.add_files_button, 0, 0)
        controls.addWidget(self.load_tray_button, 0, 1)
        controls.addWidget(self.save_tray_button, 0, 2)
        controls.addWidget(self.remove_selected_button, 0, 3)
        controls.addWidget(self.move_up_button, 1, 0)
        controls.addWidget(self.move_down_button, 1, 1)
        controls.addWidget(self.clear_button, 1, 2)
        controls.setColumnStretch(4, 1)
        root.addLayout(controls)

        self.file_list = DragDropList()
        self.file_list.setSelectionMode(DragDropList.SelectionMode.ExtendedSelection)
        root.addWidget(self.file_list)

        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        search_row.addWidget(QLabel("Keyword search"))
        self.search_query_edit = QLineEdit()
        self.search_query_edit.setPlaceholderText("Search current stitch batch")
        self.search_case_check = QCheckBox("Case sensitive")
        self.search_button = QPushButton("Search Batch")
        self.clear_search_button = QPushButton("Clear Results")
        self.search_button.setProperty("uiRole", "secondary")
        self.clear_search_button.setProperty("uiRole", "quiet")
        self.search_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        self.clear_search_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        search_row.addWidget(self.search_query_edit, 1)
        search_row.addWidget(self.search_case_check)
        search_row.addWidget(self.search_button)
        search_row.addWidget(self.clear_search_button)
        root.addLayout(search_row)

        self.search_status_label = QLabel("Search ready.")
        self.search_status_label.setObjectName("searchStatusLabel")
        root.addWidget(self.search_status_label)
        self.search_results_panel = WarningPanel()
        self.search_results_panel.setMaximumHeight(150)
        root.addWidget(self.search_results_panel)

        output_grid = QGridLayout()
        output_grid.setHorizontalSpacing(12)
        output_grid.setVerticalSpacing(10)
        output_grid.addWidget(QLabel("Output file"), 0, 0)
        self.output_path_edit = QLineEdit()
        output_grid.addWidget(self.output_path_edit, 0, 1)
        self.browse_output_button = QPushButton("Browse")
        self.browse_output_button.setProperty("uiRole", "secondary")
        self.browse_output_button.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        )
        output_grid.addWidget(self.browse_output_button, 0, 2)
        root.addLayout(output_grid)

        preview_row = QHBoxLayout()
        preview_row.setSpacing(12)
        preview_row.addWidget(QLabel("Separator preview"))
        self.separator_preview_edit = QLineEdit()
        self.separator_preview_edit.setReadOnly(True)
        preview_row.addWidget(self.separator_preview_edit)
        root.addLayout(preview_row)

        run_row = QHBoxLayout()
        run_row.setSpacing(12)
        self.stitch_button = QPushButton("Stitch")
        self.cancel_button = QPushButton("Cancel")
        self.stitch_button.setProperty("uiRole", "primary")
        self.cancel_button.setProperty("uiRole", "danger")
        self.stitch_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.cancel_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
        self.cancel_button.setEnabled(False)
        run_row.addWidget(self.stitch_button)
        run_row.addWidget(self.cancel_button)
        self.status_label = QLabel("Ready.")
        run_row.addWidget(self.status_label)
        root.addLayout(run_row)

        root.addWidget(QLabel("Duplicate basenames"))
        self.duplicate_warning_label = QLabel("")
        self.duplicate_warning_label.setWordWrap(True)
        root.addWidget(self.duplicate_warning_label)

        root.addWidget(QLabel("Warnings"))
        self.warning_panel = WarningPanel()
        root.addWidget(self.warning_panel)

        apply_button_metrics_to(self)
        self._apply_accessibility()
        self._connect_signals()

    def _apply_accessibility(self) -> None:
        self.add_files_button.setAccessibleName("Add Markdown files")
        self.add_files_button.setToolTip("Add Markdown files to the stitch list.")
        self.load_tray_button.setAccessibleName("Load stitch tray")
        self.load_tray_button.setToolTip("Load a saved stitch tray and restore its file order.")
        self.save_tray_button.setAccessibleName("Save stitch tray")
        self.save_tray_button.setToolTip("Save the current stitch list as a reusable tray.")
        self.remove_selected_button.setAccessibleName("Remove selected Markdown files")
        self.remove_selected_button.setToolTip("Remove selected files from the stitch list.")
        self.clear_button.setAccessibleName("Clear stitch list")
        self.clear_button.setToolTip("Clear the stitch list and warnings.")
        self.move_up_button.setAccessibleName("Move selected file up")
        self.move_up_button.setToolTip("Move the selected file earlier in the stitch order.")
        self.move_down_button.setAccessibleName("Move selected file down")
        self.move_down_button.setToolTip("Move the selected file later in the stitch order.")

        self.file_list.setAccessibleName("Markdown stitch list")
        self.file_list.setAccessibleDescription(
            "Ordered Markdown files that will be stitched together."
        )
        self.search_query_edit.setAccessibleName("Stitch batch keyword search query")
        self.search_query_edit.setToolTip("Search for a keyword or phrase in current stitch files.")
        self.search_case_check.setAccessibleName("Case sensitive stitch search")
        self.search_case_check.setToolTip("Match uppercase and lowercase exactly.")
        self.search_button.setAccessibleName("Search current stitch batch")
        self.search_button.setToolTip("Search Markdown files currently in the stitch list.")
        self.clear_search_button.setAccessibleName("Clear stitch search results")
        self.clear_search_button.setToolTip("Clear keyword search results.")
        self.search_status_label.setAccessibleName("Stitch search status")
        self.search_results_panel.setAccessibleName("Stitch search results")
        self.output_path_edit.setAccessibleName("Stitched Markdown output file")
        self.output_path_edit.setToolTip("Destination .md file for the stitched output.")
        self.browse_output_button.setAccessibleName("Browse for stitched Markdown output file")
        self.browse_output_button.setToolTip("Choose where to save the stitched Markdown file.")
        self.separator_preview_edit.setAccessibleName("Separator preview")
        self.separator_preview_edit.setToolTip(
            "Preview of the separator inserted after the selected file."
        )

        self.stitch_button.setAccessibleName("Start Markdown stitching")
        self.stitch_button.setToolTip("Build one Markdown document from the ordered list.")
        self.cancel_button.setAccessibleName("Cancel active stitching")
        self.cancel_button.setToolTip("Request cancellation of the active stitch run.")
        self.status_label.setAccessibleName("Stitcher status")
        self.duplicate_warning_label.setAccessibleName("Duplicate basename warnings")
        self.warning_panel.setAccessibleName("Stitcher warnings and errors")

    def _connect_signals(self) -> None:
        self.add_files_button.clicked.connect(self._on_add_files)
        self.load_tray_button.clicked.connect(self._on_load_tray)
        self.save_tray_button.clicked.connect(self._on_save_tray)
        self.remove_selected_button.clicked.connect(self._on_remove_selected)
        self.clear_button.clicked.connect(self._on_clear)
        self.move_up_button.clicked.connect(self._on_move_up)
        self.move_down_button.clicked.connect(self._on_move_down)
        self.browse_output_button.clicked.connect(self._on_pick_output)
        self.stitch_button.clicked.connect(self._on_stitch)
        self.cancel_button.clicked.connect(self._on_cancel)
        self.search_button.clicked.connect(self._on_search_batch)
        self.clear_search_button.clicked.connect(self._on_clear_search_results)
        self.search_query_edit.returnPressed.connect(self._on_search_batch)
        self.file_list.dropped_paths.connect(self._on_paths_dropped)
        self.file_list.currentRowChanged.connect(self._refresh_separator_preview)
        model = self.file_list.model()
        model.rowsMoved.connect(self._on_list_structure_changed)
        model.rowsInserted.connect(self._on_list_structure_changed)
        model.rowsRemoved.connect(self._on_list_structure_changed)

    def _on_add_files(self) -> None:
        if self._is_stitching:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Markdown files",
            "",
            "Markdown Files (*.md *.markdown)",
        )
        self._add_paths([Path(file) for file in files])

    def _on_paths_dropped(self, paths: list[str]) -> None:
        if self._is_stitching:
            return
        self._add_paths([Path(item) for item in paths])

    def _on_remove_selected(self) -> None:
        if self._is_stitching:
            return
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
        self._refresh_separator_preview()
        self._refresh_duplicate_warnings()

    def _on_load_tray(self) -> None:
        if self._is_stitching:
            return
        tray_file, _ = QFileDialog.getOpenFileName(
            self,
            "Load stitch tray",
            "",
            TRAY_FILE_FILTER,
        )
        if not tray_file:
            return

        try:
            tray = load_stitch_tray(Path(tray_file))
        except StitchTrayError as exc:
            QMessageBox.critical(self, "Load tray failed", str(exc))
            self._append_warning(f"Tray load failed: {exc}")
            return

        valid_paths: list[Path] = []
        skipped_paths: list[str] = []
        for path in tray.input_files:
            suffix = path.suffix.lower()
            if suffix not in {".md", ".markdown"}:
                skipped_paths.append(f"{path} (not markdown)")
                continue
            if not path.exists():
                skipped_paths.append(f"{path} (missing)")
                continue
            valid_paths.append(path)

        if not valid_paths:
            QMessageBox.warning(
                self,
                "Load tray",
                "Tray did not contain any usable markdown files.",
            )
            for skipped in skipped_paths:
                self._append_warning(f"Skipped tray item: {skipped}")
            return

        if self.file_list.count() > 0:
            choice = QMessageBox.question(
                self,
                "Load tray",
                "Replace the current stitch list with the loaded tray?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if choice != QMessageBox.StandardButton.Yes:
                return

        self.file_list.clear()
        self.warning_panel.clear()
        self.duplicate_warning_label.clear()
        self._add_paths(valid_paths)
        if tray.output_path is not None:
            self.output_path_edit.setText(str(tray.output_path))

        for skipped in skipped_paths:
            self._append_warning(f"Skipped tray item: {skipped}")
        self.status_label.setText(f"Loaded tray with {len(valid_paths)} file(s).")

    def _on_save_tray(self) -> None:
        if self._is_stitching:
            return
        input_paths = self._collect_input_paths()
        if not input_paths:
            QMessageBox.warning(
                self,
                "Save tray",
                "Add at least one markdown file before saving a tray.",
            )
            return

        output_text = self.output_path_edit.text().strip()
        output_path = Path(output_text) if output_text else None
        tray_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save stitch tray",
            "",
            TRAY_FILE_FILTER,
        )
        if not tray_file:
            return

        tray_path = Path(tray_file)
        if tray_path.suffix.lower() != ".json":
            tray_path = tray_path.with_suffix(TRAY_FILE_SUFFIX)
        elif not tray_path.name.lower().endswith(TRAY_FILE_SUFFIX):
            tray_path = tray_path.with_name(f"{tray_path.stem}{TRAY_FILE_SUFFIX}")

        try:
            save_stitch_tray(
                tray_path,
                input_files=input_paths,
                output_path=output_path,
            )
        except StitchTrayError as exc:
            QMessageBox.critical(self, "Save tray failed", str(exc))
            self._append_warning(f"Tray save failed: {exc}")
            return

        self.status_label.setText(f"Tray saved: {tray_path.name}")

    def _on_clear(self) -> None:
        if self._is_stitching:
            return
        self.file_list.clear()
        self.separator_preview_edit.clear()
        self.duplicate_warning_label.clear()
        self.warning_panel.clear()
        self.search_results_panel.clear()
        self.search_status_label.setText("Search ready.")

    def _on_move_up(self) -> None:
        if self._is_stitching:
            return
        row = self.file_list.currentRow()
        if row <= 0:
            return
        item = self.file_list.takeItem(row)
        self.file_list.insertItem(row - 1, item)
        self.file_list.setCurrentRow(row - 1)
        self._refresh_duplicate_warnings()

    def _on_move_down(self) -> None:
        if self._is_stitching:
            return
        row = self.file_list.currentRow()
        if row < 0 or row >= self.file_list.count() - 1:
            return
        item = self.file_list.takeItem(row)
        self.file_list.insertItem(row + 1, item)
        self.file_list.setCurrentRow(row + 1)
        self._refresh_duplicate_warnings()

    def _on_pick_output(self) -> None:
        if self._is_stitching:
            return
        target, _ = QFileDialog.getSaveFileName(
            self,
            "Choose output markdown file",
            "",
            "Markdown Files (*.md)",
        )
        if target:
            if not target.lower().endswith(".md"):
                target = f"{target}.md"
            self.output_path_edit.setText(target)

    def _on_stitch(self) -> None:
        if self._is_stitching:
            return

        input_paths = self._collect_input_paths()
        output_text = self.output_path_edit.text().strip()

        if not input_paths:
            QMessageBox.warning(self, "Stitcher", "Add at least one markdown file.")
            return
        if not output_text:
            QMessageBox.warning(self, "Stitcher", "Choose an output .md file.")
            return

        try:
            StitchManifest(input_files=input_paths, output_path=Path(output_text))
        except (ValueError, StitcherValidationError) as exc:
            QMessageBox.critical(self, "Stitch failed", str(exc))
            self.status_label.setText("Stitch failed.")
            return

        self._cancel_requested = False
        self._set_stitch_running_state(True)
        self.status_label.setText("Stitching...")
        self._play_sound("start")
        self._start_worker(input_paths, Path(output_text))

    def _on_cancel(self) -> None:
        if not self._is_stitching:
            return
        self._cancel_requested = True
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Cancelling...")
        if self._active_worker is not None:
            self._active_worker.cancel()

    def _on_search_batch(self) -> None:
        if self._is_searching:
            return
        query = self.search_query_edit.text().strip()
        if not query:
            QMessageBox.warning(self, "Keyword search", "Enter a keyword or phrase first.")
            return
        input_paths = self._collect_input_paths()
        if not input_paths:
            QMessageBox.information(self, "Keyword search", "Stitch list is empty.")
            return

        self.search_results_panel.setPlainText("Searching stitch files...")
        self.search_status_label.setText("Searching...")
        self._set_search_running_state(True)
        self._play_sound("start")
        self._start_search_worker(
            [str(path) for path in input_paths],
            query,
            self.search_case_check.isChecked(),
        )

    def _on_clear_search_results(self) -> None:
        if self._is_searching:
            return
        self.search_results_panel.clear()
        self.search_status_label.setText("Search ready.")

    def _start_search_worker(
        self,
        input_paths: list[str],
        query: str,
        case_sensitive: bool,
    ) -> None:
        worker = SearchWorker(
            input_files=input_paths,
            query=query,
            settings=load_settings(),
            case_sensitive=case_sensitive,
        )
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self._on_search_progress)
        worker.finished.connect(self._on_search_finished)
        worker.failed.connect(self._on_search_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_search_thread_finished)

        self._active_search_worker = worker
        self._active_search_thread = thread
        thread.start()

    def _on_search_progress(self, index: int, total: int, _: object) -> None:
        self.search_status_label.setText(f"Searching {index}/{total}...")

    def _on_search_finished(self, summary: object) -> None:
        self.search_results_panel.setPlainText(format_search_summary(summary))
        self.search_status_label.setText(
            f"{summary.total_matches} match(es) in {summary.files_with_matches} file(s)."
        )
        self._play_sound("complete" if summary.total_matches else "warning")

    def _on_search_failed(self, message: str) -> None:
        self.search_results_panel.setPlainText(f"Search failed: {message}")
        self.search_status_label.setText("Search failed.")
        self._play_sound("warning")

    def _on_search_thread_finished(self) -> None:
        self._active_search_worker = None
        self._active_search_thread = None
        self._set_search_running_state(False)

    def _set_search_running_state(self, running: bool) -> None:
        self._is_searching = running
        self.search_query_edit.setEnabled(not running)
        self.search_case_check.setEnabled(not running)
        self.search_button.setEnabled(not running)
        self.clear_search_button.setEnabled(not running)

    def _start_worker(self, input_paths: list[Path], output_path: Path) -> None:
        worker = StitchWorker(
            input_files=[str(path) for path in input_paths],
            output_file=str(output_path),
        )
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(self._on_worker_finished)
        worker.failed.connect(self._on_worker_failed)
        worker.cancelled.connect(self._on_worker_cancelled)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.cancelled.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_worker_thread_finished)

        self._active_worker = worker
        self._active_thread = thread
        thread.start()

    def _on_worker_finished(self, result: StitchResult) -> None:
        warning_note = ""
        if result.warnings:
            warning_note = f" with {len(result.warnings)} warning(s)"
            for warning in result.warnings:
                self._append_warning(f"[{warning.code}] {warning.message}")
        QMessageBox.information(
            self,
            "Stitch complete",
            f"Created {result.output_path}{warning_note}.",
        )
        self.status_label.setText(f"Stitched {result.file_count} file(s).")
        self._play_sound("complete" if not result.warnings else "warning")
        self._cancel_requested = False

    def _on_worker_failed(self, message: str) -> None:
        QMessageBox.critical(self, "Stitch failed", message)
        self._append_warning(message)
        self.status_label.setText("Stitch failed.")
        self._play_sound("warning")
        self._cancel_requested = False

    def _on_worker_cancelled(self, message: str) -> None:
        QMessageBox.information(self, "Stitch cancelled", message)
        self._append_warning(message)
        self.status_label.setText("Stitch cancelled.")
        self._play_sound("warning")
        self._cancel_requested = False

    def _on_worker_thread_finished(self) -> None:
        self._active_worker = None
        self._active_thread = None
        self._set_stitch_running_state(False)

    def _set_stitch_running_state(self, running: bool) -> None:
        self._is_stitching = running
        self.add_files_button.setEnabled(not running)
        self.load_tray_button.setEnabled(not running)
        self.save_tray_button.setEnabled(not running)
        self.remove_selected_button.setEnabled(not running)
        self.clear_button.setEnabled(not running)
        self.move_up_button.setEnabled(not running)
        self.move_down_button.setEnabled(not running)
        self.browse_output_button.setEnabled(not running)
        self.file_list.setEnabled(not running)
        self.output_path_edit.setEnabled(not running)
        self.stitch_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)

    def _collect_input_paths(self) -> list[Path]:
        return [Path(self.file_list.item(i).text()) for i in range(self.file_list.count())]

    def _add_paths(self, paths: list[Path]) -> None:
        for path in paths:
            suffix = path.suffix.lower()
            if suffix not in {".md", ".markdown"}:
                self._append_warning(f"Ignored non-markdown input: {path.name}")
                continue
            self.file_list.addItem(str(path))
        if self.file_list.count() > 0 and self.file_list.currentRow() < 0:
            self.file_list.setCurrentRow(0)
        self._refresh_separator_preview()
        self._refresh_duplicate_warnings()

    def _on_list_structure_changed(self, *_: object) -> None:
        self._refresh_separator_preview()
        self._refresh_duplicate_warnings()

    def _refresh_separator_preview(self) -> None:
        row = self.file_list.currentRow()
        if row < 0:
            self.separator_preview_edit.clear()
            return
        item = self.file_list.item(row)
        if item is None:
            self.separator_preview_edit.clear()
            return
        name = Path(item.text()).name
        self.separator_preview_edit.setText(build_separator(name))

    def _refresh_duplicate_warnings(self) -> None:
        names = [
            Path(self.file_list.item(i).text()).name.lower()
            for i in range(self.file_list.count())
        ]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if not duplicates:
            self.duplicate_warning_label.clear()
            return
        lines = [
            f"[DUPLICATE_BASENAME] duplicate basename in stitch list: {name}" for name in duplicates
        ]
        self.duplicate_warning_label.setText("\n".join(lines))

    def _append_warning(self, message: str) -> None:
        current = self.warning_panel.toPlainText()
        if current:
            self.warning_panel.append(message)
        else:
            self.warning_panel.setPlainText(message)

    def _play_sound(self, name: str) -> None:
        window = self.window()
        play_sound = getattr(window, "play_sound", None)
        if callable(play_sound):
            play_sound(name)
