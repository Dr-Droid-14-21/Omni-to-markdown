from __future__ import annotations

from PySide6.QtWidgets import QTextEdit


class WarningPanel(QTextEdit):
    """Read-only warning panel placeholder."""

    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
