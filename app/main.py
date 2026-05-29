from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from app.core.logging_config import configure_logging
from app.core.paths import ensure_app_dirs
from app.ui.main_window import MainWindow


def _load_stylesheet() -> str:
    style_path = Path(__file__).parent / "resources" / "styles" / "app.qss"
    if not style_path.exists():
        return ""
    return style_path.read_text(encoding="utf-8")


def _build_splash() -> QSplashScreen:
    pixmap = QPixmap(760, 360)
    pixmap.fill(QColor("#050505"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.fillRect(0, 0, 760, 360, QColor("#050505"))
    painter.setPen(QColor("#FFD700"))
    painter.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
    painter.drawText(42, 112, "OMNI TO MARKDOWN")
    painter.setPen(QColor("#F5F5DC"))
    painter.setFont(QFont("Segoe UI", 11))
    painter.drawText(44, 156, "Loading local document engines")
    painter.setPen(QColor("#CC7722"))
    painter.drawLine(44, 206, 716, 206)
    painter.setPen(QColor("#F5F5DC"))
    painter.drawText(44, 248, "Preparing converter, stitcher, search, and reports...")
    painter.end()

    splash = QSplashScreen(pixmap)
    splash.setWindowTitle("Omni to Markdown")
    return splash


def main() -> int:
    ensure_app_dirs()
    configure_logging()

    app = QApplication(sys.argv)
    stylesheet = _load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    splash = _build_splash()
    splash.show()
    app.processEvents()

    window = MainWindow()

    def show_main_window() -> None:
        window.show()
        splash.finish(window)

    QTimer.singleShot(650, show_main_window)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
