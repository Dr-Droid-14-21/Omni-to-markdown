from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QFrame, QSizePolicy, QWidget

from app.ui.widgets.sci_fi_corners import create_stepped_bevel_path


class CutCornerPanel(QFrame):
    """A lightweight Neon-GX panel with real diagonal corner cuts."""

    def __init__(self, parent: QWidget | None = None, *, cut: int = 12) -> None:
        super().__init__(parent)
        self._cut = cut
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        cut = min(self._cut, int(rect.width() // 3), int(rect.height() // 3))

        path = create_stepped_bevel_path(rect, cut)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QColor("#08151e"))
        gradient.setColorAt(0.48, QColor("#0a1b25"))
        gradient.setColorAt(1.0, QColor("#061019"))

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillPath(path, gradient)
        painter.setPen(QPen(QColor(20, 242, 255, 96), 1))
        painter.drawPath(path)

        accent = min(cut + 8, 22)
        painter.setPen(QPen(QColor("#22f4ff"), 2))
        painter.drawLine(
            QPointF(rect.left() + 1, rect.top() + accent),
            QPointF(rect.left() + accent, rect.top() + 1),
        )
        painter.setPen(QPen(QColor("#ff2e67"), 1))
        painter.drawLine(
            QPointF(rect.left() + 6, rect.top() + accent + 3),
            QPointF(rect.left() + accent + 3, rect.top() + 6),
        )
        painter.setPen(QPen(QColor(35, 244, 255, 76), 1))
        painter.drawLine(
            QPointF(rect.right() - accent, rect.bottom() - 1),
            QPointF(rect.right() - 1, rect.bottom() - accent),
        )
        painter.end()
