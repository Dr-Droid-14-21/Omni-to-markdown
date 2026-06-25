from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QDragEnterEvent,
    QDragLeaveEvent,
    QDragMoveEvent,
    QDropEvent,
    QLinearGradient,
    QPainter,
    QPaintEvent,
    QPen,
)
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from app.ui.widgets.sci_fi_corners import create_stepped_bevel_path


class FileQueueTable(QTableWidget):
    HEADERS = ["File", "Type", "Status", "Engine Route", "Warnings"]
    EMPTY_STATE_TITLE = "Drop documents or folders here"
    EMPTY_STATE_DETAIL = (
        ".doc, .docx, .htm, .html, .pdf, .odt, .odf, .rtf, and .txt convert to Markdown"
    )
    ACTIVE_DROP_TITLE = "Release to queue for Markdown conversion"
    ACTIVE_DROP_DETAIL = "Omni will expand folders, skip unsupported files, and preserve sources."
    dropped_paths = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._drag_active = False
        self.setColumnCount(len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setMinimumHeight(200)

        self._scan_timer = QTimer(self)
        self._scan_timer.setInterval(30)
        self._scan_timer.timeout.connect(self.viewport().update)
        self._scan_offset = 0.0

    def empty_state_text(self) -> str:
        title, detail = self._empty_state_copy()
        return f"{title}\n{detail}"

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

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        if self.rowCount() > 0:
            return

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.viewport().rect().adjusted(18, 18, -18, -18)
        title, detail = self._empty_state_copy()
        
        cut = 14
        path = create_stepped_bevel_path(rect, cut)

        if self._drag_active:
            painter.setPen(QPen(QColor("#7cfbff"), 2))
            
            # Sci-Fi Scanning Fill
            self._scan_offset += 2.0
            if self._scan_offset > rect.height():
                self._scan_offset = 0.0
                
            grad = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
            grad.setColorAt(0.0, QColor(8, 36, 46, 172))
            scan_y = self._scan_offset / max(1.0, rect.height())
            grad.setColorAt(min(1.0, max(0.0, scan_y)), QColor(21, 244, 255, 120))
            grad.setColorAt(1.0, QColor(8, 36, 46, 172))
            
            painter.fillPath(path, grad)
            
            # Draw actual scan line
            painter.setPen(QPen(QColor(21, 244, 255, 200), 2))
            scan_line_y = rect.top() + self._scan_offset
            painter.drawLine(rect.left() + cut, scan_line_y, rect.right() - cut, scan_line_y)
        else:
            painter.setPen(QPen(QColor(26, 79, 92), 1))
            painter.fillPath(path, QColor(5, 13, 19, 96))
        border_color = QColor("#7cfbff") if self._drag_active else QColor(26, 79, 92)
        border_width = 2 if self._drag_active else 1
        painter.setPen(QPen(border_color, border_width))
        painter.drawPath(path)

        painter.setPen(QColor("#f6ffff" if self._drag_active else "#1ff4ff"))
        font = painter.font()
        font.setPointSize(max(font.pointSize() + 4, 13))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            title,
        )

        detail_rect = rect.adjusted(0, 52, 0, 0)
        detail_font = painter.font()
        detail_font.setPointSize(max(detail_font.pointSize() - 5, 9))
        detail_font.setBold(False)
        painter.setFont(detail_font)
        painter.setPen(QColor("#b7f7ff" if self._drag_active else "#7ea8b2"))
        painter.drawText(
            detail_rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            detail,
        )
        painter.end()

    def _find_row_by_path(self, path_value: str) -> int | None:
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item is None:
                continue
            value = item.data(Qt.ItemDataRole.UserRole)
            if value == path_value:
                return row
        return None

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            self._set_drag_active(True)
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.mimeData().hasUrls():
            self._set_drag_active(True)
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        self._set_drag_active(False)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            paths = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if url.isLocalFile() and url.toLocalFile()
            ]
            if paths:
                self._set_drag_active(False)
                self.dropped_paths.emit(paths)
                event.acceptProposedAction()
                return
        self._set_drag_active(False)
        super().dropEvent(event)

    def _empty_state_copy(self) -> tuple[str, str]:
        if self._drag_active:
            return self.ACTIVE_DROP_TITLE, self.ACTIVE_DROP_DETAIL
        return self.EMPTY_STATE_TITLE, self.EMPTY_STATE_DETAIL

    def _set_drag_active(self, active: bool) -> None:
        if self._drag_active == active:
            return
        self._drag_active = active
        self.setProperty("dragActive", active)
        if active:
            self._scan_timer.start()
        else:
            self._scan_timer.stop()
        self.viewport().update()
