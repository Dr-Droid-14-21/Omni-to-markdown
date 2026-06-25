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
from PySide6.QtWidgets import QListWidget

from app.ui.widgets.sci_fi_corners import create_stepped_bevel_path


class DragDropList(QListWidget):
    EMPTY_STATE_TITLE = "Drop Markdown files here"
    EMPTY_STATE_DETAIL = "Arrange files by dragging rows, or drop .md files from Explorer."
    ACTIVE_DROP_TITLE = "Release to add Markdown files"
    ACTIVE_DROP_DETAIL = "Omni will keep your order editable before stitching."
    dropped_paths = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._drag_active = False
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setMinimumHeight(160)
        
        self._scan_timer = QTimer(self)
        self._scan_timer.setInterval(30)
        self._scan_timer.timeout.connect(self.viewport().update)
        self._scan_offset = 0.0

    def empty_state_text(self) -> str:
        title, detail = self._empty_state_copy()
        return f"{title}\n{detail}"

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        if self.count() > 0:
            return

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.viewport().rect().adjusted(18, 18, -18, -18)
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

        title, detail = self._empty_state_copy()
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

        detail_rect = rect.adjusted(0, 48, 0, 0)
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

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls() or event.source() is self:
            self._set_drag_active(event.mimeData().hasUrls())
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.mimeData().hasUrls() or event.source() is self:
            self._set_drag_active(event.mimeData().hasUrls())
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        self._set_drag_active(False)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if event.source() is self:
            self._set_drag_active(False)
            super().dropEvent(event)
            return

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
