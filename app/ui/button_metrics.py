from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton, QWidget


@dataclass(frozen=True)
class ButtonMetric:
    min_height: int
    min_width: int
    icon_size: QSize


BUTTON_METRICS = {
    "hero": ButtonMetric(min_height=54, min_width=158, icon_size=QSize(26, 26)),
    "primary": ButtonMetric(min_height=50, min_width=138, icon_size=QSize(24, 24)),
    "secondary": ButtonMetric(min_height=46, min_width=124, icon_size=QSize(22, 22)),
    "quiet": ButtonMetric(min_height=46, min_width=108, icon_size=QSize(22, 22)),
    "danger": ButtonMetric(min_height=46, min_width=116, icon_size=QSize(22, 22)),
}


def apply_button_metrics(button: QPushButton) -> None:
    role = str(button.property("uiRole") or "secondary")
    metric = BUTTON_METRICS.get(role, BUTTON_METRICS["secondary"])
    button.setMinimumHeight(metric.min_height)
    button.setIconSize(metric.icon_size)

    text = button.text().strip()
    if not text:
        return

    text_width = button.fontMetrics().horizontalAdvance(text)
    readable_width = text_width + metric.icon_size.width() + 48
    button.setMinimumWidth(max(metric.min_width, readable_width))


def apply_button_metrics_to(container: QWidget) -> None:
    for button in container.findChildren(QPushButton):
        apply_button_metrics(button)
