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
    "hero": ButtonMetric(min_height=46, min_width=142, icon_size=QSize(22, 22)),
    "primary": ButtonMetric(min_height=44, min_width=126, icon_size=QSize(22, 22)),
    "secondary": ButtonMetric(min_height=40, min_width=112, icon_size=QSize(20, 20)),
    "quiet": ButtonMetric(min_height=40, min_width=98, icon_size=QSize(20, 20)),
    "danger": ButtonMetric(min_height=40, min_width=108, icon_size=QSize(20, 20)),
}


def apply_button_metrics(button: QPushButton) -> None:
    role = str(button.property("uiRole") or "secondary")
    metric = BUTTON_METRICS.get(role, BUTTON_METRICS["secondary"])
    button.setMinimumHeight(metric.min_height)
    button.setMaximumHeight(metric.min_height)
    button.setIconSize(metric.icon_size)

    text = button.text().strip()
    if not text:
        return

    text_width = button.fontMetrics().horizontalAdvance(text)
    readable_width = text_width + metric.icon_size.width() + 38
    button.setMinimumWidth(max(metric.min_width, readable_width))


def apply_button_metrics_to(container: QWidget) -> None:
    for button in container.findChildren(QPushButton):
        apply_button_metrics(button)
