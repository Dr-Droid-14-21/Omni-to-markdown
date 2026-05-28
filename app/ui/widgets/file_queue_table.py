from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class FileQueueTable(QTableWidget):
    HEADERS = ["File", "Type", "Status", "Engine Route", "Warnings"]

    def __init__(self) -> None:
        super().__init__()
        self.setColumnCount(len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)

    def add_row(
        self,
        *,
        file_name: str,
        file_type: str,
        status: str,
        engine_route: str,
        warning_count: int,
        path_value: str,
    ) -> None:
        row = self.rowCount()
        self.insertRow(row)

        warning_text = str(warning_count)
        items = [
            QTableWidgetItem(file_name),
            QTableWidgetItem(file_type),
            QTableWidgetItem(status),
            QTableWidgetItem(engine_route),
            QTableWidgetItem(warning_text),
        ]
        for col, item in enumerate(items):
            if col == 4:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, path_value)
            self.setItem(row, col, item)

    def selected_paths(self) -> list[str]:
        rows = sorted({index.row() for index in self.selectedIndexes()})
        paths: list[str] = []
        for row in rows:
            item = self.item(row, 0)
            if item is None:
                continue
            value = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(value, str):
                paths.append(value)
        return paths

    def queued_extensions(self) -> set[str]:
        extensions: set[str] = set()
        for row in range(self.rowCount()):
            item = self.item(row, 1)
            if item is None:
                continue
            ext = item.text().strip().lower()
            if ext:
                extensions.add(ext)
        return extensions

    def queued_paths(self) -> list[str]:
        paths: list[str] = []
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item is None:
                continue
            value = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(value, str):
                paths.append(value)
        return paths

    def set_status_for_path(self, path_value: str, status: str) -> None:
        row = self._find_row_by_path(path_value)
        if row is None:
            return
        status_item = self.item(row, 2)
        if status_item is not None:
            status_item.setText(status)

    def set_warning_count_for_path(self, path_value: str, warning_count: int) -> None:
        row = self._find_row_by_path(path_value)
        if row is None:
            return
        warning_item = self.item(row, 4)
        if warning_item is not None:
            warning_item.setText(str(warning_count))

    def _find_row_by_path(self, path_value: str) -> int | None:
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item is None:
                continue
            value = item.data(Qt.ItemDataRole.UserRole)
            if value == path_value:
                return row
        return None
