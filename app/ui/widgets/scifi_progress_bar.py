from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QProgressBar, QWidget

from app.ui.widgets.sci_fi_corners import create_stepped_bevel_path


class SciFiProgressBar(QProgressBar):
    """A futuristic conversion bar with load FX and glowing cells."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTextVisible(False)
        self.setMinimumHeight(16)
        self.setMaximumHeight(20)
        
        self._glow_animation = QPropertyAnimation(self, b"glowIntensity", self)
        self._glow_intensity = 0.0
        self._glow_animation.setStartValue(0.0)
        self._glow_animation.setEndValue(1.0)
        self._glow_animation.setDuration(1200)
        self._glow_animation.setLoopCount(-1)  # infinite
        self._glow_animation.setEasingCurve(QEasingCurve.Type.InOutSine)

    def start_fx(self) -> None:
        if self._glow_animation.state() != QPropertyAnimation.State.Running:
            self._glow_animation.start()

    def stop_fx(self) -> None:
        self._glow_animation.stop()
        self._glow_intensity = 0.0
        self.update()

    def get_glow_intensity(self) -> float:
        return self._glow_intensity

    def set_glow_intensity(self, value: float) -> None:
        self._glow_intensity = value
        self.update()

    # PySide6 property system hook
    glowIntensity = property(get_glow_intensity, set_glow_intensity)

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        cut = 6
        path = create_stepped_bevel_path(rect, cut)

        # Draw background shell
        painter.setBrush(QColor(5, 13, 19, 150))
        painter.setPen(QPen(QColor(26, 79, 92, 100), 1))
        painter.drawPath(path)

        if self.maximum() <= 0:
            return

        progress = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        if progress <= 0:
            return

        # Calculate fill rect
        fill_width = max(rect.width() * progress, cut * 2 + 1)
        fill_rect = QRectF(rect.left(), rect.top(), fill_width, rect.height())
        fill_path = create_stepped_bevel_path(fill_rect, cut)

        # Sci-Fi segmented fill (cells)
        # Using a gradient that pulses with the glow intensity
        base_color = QColor(21, 244, 255)
        pulse = 150 + int(105 * self._glow_intensity)
        base_color.setAlpha(pulse)

        gradient = QLinearGradient(fill_rect.topLeft(), fill_rect.bottomRight())
        gradient.setColorAt(0.0, QColor(8, 36, 46, 200))
        gradient.setColorAt(0.8, base_color)
        gradient.setColorAt(1.0, QColor(255, 255, 255, pulse))

        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(fill_path)

        # Draw segmented lines over the fill path
        painter.setPen(QPen(QColor(5, 13, 19), 2))
        segment_width = 20
        x = rect.left() + segment_width
        while x < fill_rect.right():
            painter.drawLine(x + 4, rect.top(), x - 4, rect.bottom())
            x += segment_width

        painter.end()
