from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from app.conversion.dependency_check import (
    dependency_route_options_for_extension,
    detect_all_dependencies,
)
from app.conversion.reports import build_run_report, write_run_reports
from app.conversion.router import build_plan
from app.core.file_detection import (
    SUPPORTED_EXTENSIONS,
    check_output_directory_writable,
    detect_file,
)
from app.core.models import ConversionResult
from app.core.settings import load_settings
from app.search import format_search_summary
from app.ui.button_metrics import apply_button_metrics_to
from app.ui.widgets.file_queue_table import FileQueueTable
from app.ui.widgets.warning_panel import WarningPanel
from app.workers.conversion_worker import ConversionWorker
from app.workers.search_worker import SearchWorker


class ConverterTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._paths_in_queue: set[str] = set()
        self._preflight_ok = False
        self._is_converting = False
        self._cancel_requested = False
        self._retry_failed_paths: set[str] = set()
        self._settings = load_settings()
        self._active_thread: QThread | None = None
        self._active_worker: ConversionWorker | None = None
        self._is_searching = False
        self._active_search_thread: QThread | None = None
        self._active_search_worker: SearchWorker | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("converterTab")
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title = QLabel("OMNI CONVERTER // LOCAL DOCUMENT PIPELINE")
        title.setObjectName("tabTitle")
        root.addWidget(title)
        subtitle = QLabel("Queue supported documents, verify engines, then convert to Markdown.")
        subtitle.setObjectName("tabSubtitle")
        root.addWidget(subtitle)

        top_actions = QHBoxLayout()
        top_actions.setSpacing(12)
        self.add_files_button = QPushButton("Add Files")
        self.add_folder_button = QPushButton("Add Folder")
        self.remove_button = QPushButton("Remove")
        self.clear_button = QPushButton("Clear")
        self.add_files_button.setProperty("uiRole", "hero")
        self.add_folder_button.setProperty("uiRole", "hero")
        self.remove_button.setProperty("uiRole", "secondary")
        self.clear_button.setProperty("uiRole", "quiet")
        style = self.style()
        self.add_files_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.add_folder_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        self.remove_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.clear_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        top_actions.addWidget(self.add_files_button)
        top_actions.addWidget(self.add_folder_button)
        top_actions.addWidget(self.remove_button)
        top_actions.addWidget(self.clear_button)
        root.addLayout(top_actions)

        output_row = QHBoxLayout()
        output_row.setSpacing(12)
        output_row.addWidget(QLabel("Output folder"))
        self.output_folder_edit = QLineEdit(self._settings.default_output_directory)
        self.browse_output_button = QPushButton("Browse")
        self.browse_output_button.setProperty("uiRole", "secondary")
        self.browse_output_button.setIcon(
            style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        )
        output_row.addWidget(self.output_folder_edit)
        output_row.addWidget(self.browse_output_button)
        root.addLayout(output_row)

        self.queue_table = FileQueueTable()
        root.addWidget(self.queue_table)

        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        search_row.addWidget(QLabel("Keyword search"))
        self.search_query_edit = QLineEdit()
        self.search_query_edit.setPlaceholderText("Search current conversion batch")
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

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.preflight_button = QPushButton("Run Preflight")
        self.convert_button = QPushButton("Convert")
        self.cancel_button = QPushButton("Cancel")
        self.retry_failed_button = QPushButton("Retry Failed")
        self.preflight_button.setProperty("uiRole", "primary")
        self.convert_button.setProperty("uiRole", "primary")
        self.cancel_button.setProperty("uiRole", "danger")
        self.retry_failed_button.setProperty("uiRole", "secondary")
        self.preflight_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.convert_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.cancel_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
        self.retry_failed_button.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.convert_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.retry_failed_button.setEnabled(False)
        action_row.addWidget(self.preflight_button)
        action_row.addWidget(self.convert_button)
        action_row.addWidget(self.cancel_button)
        action_row.addWidget(self.retry_failed_button)
        root.addLayout(action_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        root.addWidget(self.progress_bar)

        root.addWidget(QLabel("Warnings"))
        self.warning_panel = WarningPanel()
        root.addWidget(self.warning_panel)

        apply_button_metrics_to(self)
        self._apply_accessibility()
        self._connect_signals()

    def _apply_accessibility(self) -> None:
        self.add_files_button.setAccessibleName("Add document files")
        self.add_files_button.setToolTip("Add individual documents to the conversion queue.")
        self.add_folder_button.setAccessibleName("Add document folder")
        self.add_folder_button.setToolTip("Add all supported documents from a folder.")
        self.remove_button.setAccessibleName("Remove selected queued files")
        self.remove_button.setToolTip("Remove selected rows from the conversion queue.")
        self.clear_button.setAccessibleName("Clear conversion queue")
        self.clear_button.setToolTip("Remove every queued document and clear warnings.")

        self.output_folder_edit.setAccessibleName("Conversion output folder")
        self.output_folder_edit.setToolTip(
            "Folder where converted Markdown files and reports are written."
        )
        self.browse_output_button.setAccessibleName("Browse for conversion output folder")
        self.browse_output_button.setToolTip("Choose the output folder.")
        self.queue_table.setAccessibleName("Conversion queue")
        self.queue_table.setAccessibleDescription(
            "Queued source files with type, status, selected engine route, and warning count."
        )
        self.search_query_edit.setAccessibleName("Batch keyword search query")
        self.search_query_edit.setToolTip("Search for a keyword or phrase in queued files.")
        self.search_case_check.setAccessibleName("Case sensitive batch search")
        self.search_case_check.setToolTip("Match uppercase and lowercase exactly.")
        self.search_button.setAccessibleName("Search current conversion batch")
        self.search_button.setToolTip("Search queued files using Markdown reading and Apache Tika.")
        self.clear_search_button.setAccessibleName("Clear batch search results")
        self.clear_search_button.setToolTip("Clear keyword search results.")
        self.search_status_label.setAccessibleName("Batch search status")
        self.search_results_panel.setAccessibleName("Batch search results")

        self.preflight_button.setAccessibleName("Run conversion preflight")
        self.preflight_button.setToolTip(
            "Check queued files and required engines before conversion."
        )
        self.convert_button.setAccessibleName("Start conversion")
        self.convert_button.setToolTip("Convert queued documents after preflight passes.")
        self.cancel_button.setAccessibleName("Cancel active conversion")
        self.cancel_button.setToolTip("Request cancellation of the active conversion run.")
        self.retry_failed_button.setAccessibleName("Retry failed conversions")
        self.retry_failed_button.setToolTip(
            "Run conversion again for files that failed in the last batch."
        )

        self.progress_bar.setAccessibleName("Conversion progress")
        self.warning_panel.setAccessibleName("Conversion warnings and errors")

    def _connect_signals(self) -> None:
        self.add_files_button.clicked.connect(self._on_add_files)
        self.add_folder_button.clicked.connect(self._on_add_folder)
        self.remove_button.clicked.connect(self._on_remove_selected)
        self.clear_button.clicked.connect(self._on_clear)
        self.browse_output_button.clicked.connect(self._on_pick_output_folder)
        self.output_folder_edit.textEdited.connect(self._on_output_folder_edited)
        self.preflight_button.clicked.connect(self._run_preflight_on_queue)
        self.convert_button.clicked.connect(self._on_convert)
        self.cancel_button.clicked.connect(self._on_cancel)
        self.retry_failed_button.clicked.connect(self._on_retry_failed)
        self.search_button.clicked.connect(self._on_search_batch)
        self.clear_search_button.clicked.connect(self._on_clear_search_results)
        self.search_query_edit.returnPressed.connect(self._on_search_batch)
        self.queue_table.dropped_paths.connect(self._on_paths_dropped)

    def _on_add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select documents",
            "",
            "Documents (*.doc *.docx *.pdf *.odt *.odf);;All files (*.*)",
        )
        self._add_paths([Path(item) for item in files])

    def _on_add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if not folder:
            return
        root = Path(folder)
        self._add_paths(self._expand_supported_paths([root]))

    def _on_paths_dropped(self, paths: list[str]) -> None:
        if self._is_converting:
            return
        self._add_paths(self._expand_supported_paths([Path(item) for item in paths]))

    def _on_remove_selected(self) -> None:
        selected_rows = sorted(
            {index.row() for index in self.queue_table.selectedIndexes()},
            reverse=True,
        )
        for row in selected_rows:
            item = self.queue_table.item(row, 0)
            if item is not None:
                value = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(value, str):
                    self._paths_in_queue.discard(value)
                    self._retry_failed_paths.discard(value)
            self.queue_table.removeRow(row)
        self._mark_preflight_dirty()

    def _on_clear(self) -> None:
        self.queue_table.setRowCount(0)
        self._paths_in_queue.clear()
        self._retry_failed_paths.clear()
        self.warning_panel.clear()
        self.search_results_panel.clear()
        self.search_status_label.setText("Search ready.")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self._mark_preflight_dirty()

    def _on_pick_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select output folder")
        if folder:
            self.output_folder_edit.setText(folder)
            self._mark_preflight_dirty()

    def _on_output_folder_edited(self, _: str) -> None:
        if not self._is_converting:
            self._mark_preflight_dirty()

    def _expand_supported_paths(self, paths: list[Path]) -> list[Path]:
        candidates: list[Path] = []
        for path in paths:
            if path.is_dir():
                candidates.extend(
                    item
                    for item in path.rglob("*")
                    if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS
                )
                continue
            candidates.append(path)
        return candidates

    def _add_paths(self, paths: list[Path]) -> None:
        if not paths:
            return

        for path in paths:
            path_key = str(path.resolve())
            if path_key in self._paths_in_queue:
                continue

            detection = detect_file(path)
            if detection.error:
                self._append_warning(f"{path.name}: {detection.error}")
                continue

            output_dir = Path(self.output_folder_edit.text().strip() or ".")
            output_path = output_dir / f"{path.stem}.md"
            plan = build_plan(path, output_path)

            self.queue_table.add_row(
                file_name=path.name,
                file_type=detection.extension,
                status="Ready",
                engine_route=plan.preferred_engine,
                warning_count=len(detection.warnings) + len(plan.warnings),
                path_value=path_key,
            )
            self._paths_in_queue.add(path_key)
            for warning in detection.warnings + plan.warnings:
                self._append_warning(f"{path.name}: [{warning.code}] {warning.message}")

        self._mark_preflight_dirty()

    def _run_preflight_on_queue(self) -> None:
        if self._is_converting:
            return

        output_dir = Path(self.output_folder_edit.text().strip())
        is_writable, reason = check_output_directory_writable(output_dir)
        if not is_writable:
            QMessageBox.critical(self, "Preflight failed", reason)
            self._mark_preflight_dirty()
            return

        if self.queue_table.rowCount() == 0:
            QMessageBox.information(self, "Preflight", "Queue is empty.")
            self._mark_preflight_dirty()
            return

        self._settings = load_settings()
        dependencies = detect_all_dependencies(self._settings)
        missing: set[str] = set()
        missing_by_extension: dict[str, str] = {}
        for extension in self.queue_table.queued_extensions():
            route_options = dependency_route_options_for_extension(extension)
            route_satisfied = any(
                all(
                    not dependency or dependencies.get(dependency, None) is not None
                    and dependencies[dependency].available
                    for dependency in option
                )
                for option in route_options
            )
            if route_satisfied:
                continue
            missing_for_extension = sorted({dep for option in route_options for dep in option})
            missing.update(missing_for_extension)
            readable_options = [
                " + ".join(sorted(option)) if option else "none"
                for option in route_options
            ]
            missing_by_extension[extension] = " OR ".join(readable_options)

        if missing:
            names = ", ".join(sorted(missing))
            self._append_warning(f"Missing dependencies for queued files: {names}")
            for extension, route_text in sorted(missing_by_extension.items()):
                self._append_warning(f" - {extension}: requires {route_text}")
            for dep_name in sorted(missing):
                detail = dependencies[dep_name].detail or "Not available."
                self._append_warning(f" - {dep_name}: {detail}")
            QMessageBox.warning(
                self,
                "Preflight warnings",
                f"Missing dependencies detected: {names}. "
                "Update settings or install tools before conversion.",
            )
            self._mark_preflight_dirty()
            return

        self._preflight_ok = True
        self.convert_button.setEnabled(True)
        QMessageBox.information(
            self,
            "Preflight",
            f"Preflight passed for {self.queue_table.rowCount()} queued file(s).",
        )

    def _on_convert(self) -> None:
        if self._is_converting:
            return
        if not self._preflight_ok:
            QMessageBox.warning(self, "Conversion blocked", "Run preflight successfully first.")
            return
        if self.queue_table.rowCount() == 0:
            QMessageBox.information(self, "Conversion", "Queue is empty.")
            return

        output_dir = Path(self.output_folder_edit.text().strip())
        is_writable, reason = check_output_directory_writable(output_dir)
        if not is_writable:
            QMessageBox.critical(self, "Conversion failed", reason)
            return

        queued_paths = [Path(path) for path in self.queue_table.queued_paths()]
        for path in queued_paths:
            self.queue_table.set_status_for_path(str(path), "Converting")

        self.progress_bar.setRange(0, len(queued_paths))
        self.progress_bar.setValue(0)
        self._cancel_requested = False

        self._set_conversion_running_state(True)
        self._play_sound("start")
        self._start_worker(queued_paths, output_dir)

    def _on_cancel(self) -> None:
        if not self._is_converting:
            return
        self._cancel_requested = True
        self.cancel_button.setEnabled(False)
        if self._active_worker is not None:
            self._active_worker.cancel()
        self._append_warning("Cancellation requested. Current file may finish before queue stops.")

    def _on_retry_failed(self) -> None:
        if self._is_converting:
            return
        if not self._retry_failed_paths:
            QMessageBox.information(self, "Retry Failed", "No failed files from the last run.")
            return
        if not self._preflight_ok:
            QMessageBox.warning(
                self,
                "Retry blocked",
                "Run preflight successfully first, then retry failed files.",
            )
            return

        output_dir = Path(self.output_folder_edit.text().strip())
        is_writable, reason = check_output_directory_writable(output_dir)
        if not is_writable:
            QMessageBox.critical(self, "Retry failed", reason)
            return

        queued_paths = [Path(path) for path in self.queue_table.queued_paths()]
        retry_paths = [
            path
            for path in queued_paths
            if str(path.resolve()) in self._retry_failed_paths
        ]
        if not retry_paths:
            QMessageBox.information(self, "Retry Failed", "Failed files are no longer in queue.")
            return

        for path in retry_paths:
            self.queue_table.set_status_for_path(str(path.resolve()), "Converting")

        self.progress_bar.setRange(0, len(retry_paths))
        self.progress_bar.setValue(0)
        self._cancel_requested = False

        self._set_conversion_running_state(True)
        self._play_sound("start")
        self._start_worker(retry_paths, output_dir)

    def _on_search_batch(self) -> None:
        if self._is_searching:
            return
        query = self.search_query_edit.text().strip()
        if not query:
            QMessageBox.warning(self, "Keyword search", "Enter a keyword or phrase first.")
            return
        queued_paths = self.queue_table.queued_paths()
        if not queued_paths:
            QMessageBox.information(self, "Keyword search", "Queue is empty.")
            return

        self._settings = load_settings()
        self.search_results_panel.setPlainText("Searching queued files...")
        self.search_status_label.setText("Searching...")
        self._set_search_running_state(True)
        self._play_sound("start")
        self._start_search_worker(queued_paths, query, self.search_case_check.isChecked())

    def _on_clear_search_results(self) -> None:
        if self._is_searching:
            return
        self.search_results_panel.clear()
        self.search_status_label.setText("Search ready.")

    def _start_search_worker(
        self,
        queued_paths: list[str],
        query: str,
        case_sensitive: bool,
    ) -> None:
        worker = SearchWorker(
            input_files=queued_paths,
            query=query,
            settings=self._settings,
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

        self._active_search_thread = thread
        self._active_search_worker = worker
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

    def _start_worker(self, queued_paths: list[Path], output_dir: Path) -> None:
        worker = ConversionWorker(
            input_files=[str(path) for path in queued_paths],
            output_dir=str(output_dir),
            settings=self._settings,
        )
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self._on_worker_progress)
        worker.finished.connect(self._on_worker_finished)
        worker.failed.connect(self._on_worker_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_worker_thread_finished)

        self._active_thread = thread
        self._active_worker = worker
        thread.start()

    def _on_worker_progress(self, index: int, _: int, conversion_result: ConversionResult) -> None:
        source_key = str(conversion_result.source_path.resolve())
        status_text = self._status_text_for_result(conversion_result)
        self.queue_table.set_status_for_path(source_key, status_text)
        self.queue_table.set_warning_count_for_path(source_key, len(conversion_result.warnings))

        for warning in conversion_result.warnings:
            self._append_warning(
                f"{conversion_result.source_path.name}: [{warning.code}] {warning.message}"
            )
        for error in conversion_result.errors:
            self._append_warning(
                f"{conversion_result.source_path.name}: "
                f"[{error.code}] {error.message}"
            )
        self.progress_bar.setValue(index)

    def _on_worker_finished(
        self,
        results: list[ConversionResult],
        engine_versions: dict[str, str],
    ) -> None:
        self._retry_failed_paths = self._collect_retry_failed_paths(results)
        self.retry_failed_button.setEnabled(bool(self._retry_failed_paths))

        output_dir = Path(self.output_folder_edit.text().strip())
        report = build_run_report(results, engine_versions=engine_versions)
        json_path, markdown_path = write_run_reports(output_dir, report)
        converted = sum(
            1
            for item in results
            if item.status.value in {"converted", "converted_with_warnings"}
        )
        failed = sum(1 for item in results if item.status.value == "failed")
        cancelled = sum(1 for item in results if item.status.value == "cancelled")
        summary_title = "Conversion cancelled" if self._cancel_requested else "Conversion completed"
        QMessageBox.information(
            self,
            summary_title,
            f"Converted: {converted}, Failed: {failed}, Cancelled: {cancelled}\n"
            f"Reports:\n{json_path}\n{markdown_path}",
        )
        self._play_sound("complete" if failed == 0 and cancelled == 0 else "warning")
        self._cancel_requested = False
        self._mark_preflight_dirty()

    def _on_worker_failed(self, message: str) -> None:
        self._append_warning(f"Conversion worker failed: {message}")
        self._mark_inflight_rows_failed()
        QMessageBox.critical(self, "Conversion worker failed", message)
        self._cancel_requested = False
        self.retry_failed_button.setEnabled(False)
        self._play_sound("warning")
        self._mark_preflight_dirty()

    def _on_worker_thread_finished(self) -> None:
        self._active_worker = None
        self._active_thread = None
        self._set_conversion_running_state(False)

    def _set_conversion_running_state(self, running: bool) -> None:
        self._is_converting = running
        self.add_files_button.setEnabled(not running)
        self.add_folder_button.setEnabled(not running)
        self.remove_button.setEnabled(not running)
        self.clear_button.setEnabled(not running)
        self.browse_output_button.setEnabled(not running)
        self.output_folder_edit.setEnabled(not running)
        self.preflight_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)
        if running:
            self.convert_button.setEnabled(False)
            self.retry_failed_button.setEnabled(False)
        else:
            self.convert_button.setEnabled(self._preflight_ok and self.queue_table.rowCount() > 0)
            self.retry_failed_button.setEnabled(bool(self._retry_failed_paths))

    def _mark_inflight_rows_failed(self) -> None:
        for row in range(self.queue_table.rowCount()):
            item = self.queue_table.item(row, 2)
            if item is not None and item.text() == "Converting":
                item.setText("Failed")

    def _mark_preflight_dirty(self) -> None:
        self._preflight_ok = False
        if not self._is_converting:
            self.convert_button.setEnabled(False)
            self.cancel_button.setEnabled(False)

    def reload_settings(self) -> None:
        self._settings = load_settings()
        self.output_folder_edit.setText(self._settings.default_output_directory)
        self._mark_preflight_dirty()

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

    def _status_text_for_result(self, result: ConversionResult) -> str:
        mapping = {
            "converted": "Converted",
            "converted_with_warnings": "Converted",
            "failed": "Failed",
            "cancelled": "Cancelled",
        }
        return mapping.get(result.status.value, "Failed")

    def _collect_retry_failed_paths(self, results: list[ConversionResult]) -> set[str]:
        failed_paths = {
            str(item.source_path.resolve()) for item in results if item.status.value == "failed"
        }
        available = set(self.queue_table.queued_paths())
        return {path for path in failed_paths if path in available}
