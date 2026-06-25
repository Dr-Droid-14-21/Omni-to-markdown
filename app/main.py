from __future__ import annotations

import sys
from pathlib import Path

from app.core.logging_config import configure_logging
from app.core.paths import ensure_app_dirs
from app.launch_options import parse_launch_options
from app.self_check import write_self_check_report


def _load_stylesheet() -> str:
    style_path = Path(__file__).parent / "resources" / "styles" / "app.qss"
    if not style_path.exists():
        return ""
    return style_path.read_text(encoding="utf-8")


def _build_splash() -> object:
    from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
    from PySide6.QtWidgets import QSplashScreen

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


def main(argv: list[str] | None = None) -> int:
    runtime_argv = list(sys.argv[1:] if argv is None else argv)
    launch_options = parse_launch_options(runtime_argv)
    if launch_options.self_check:
        return write_self_check_report()

    ensure_app_dirs()
    configure_logging()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    from app.ui.main_window import MainWindow

    qt_argv = [sys.argv[0], *runtime_argv]
    app = QApplication(qt_argv)
    stylesheet = _load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    splash = None
    if not launch_options.suppress_splash:
        splash = _build_splash()
        splash.show()
        app.processEvents()

    window = MainWindow(
        initial_paths=launch_options.selected_paths,
        auto_convert=launch_options.auto_convert,
    )

    def show_main_window() -> None:
        window.show()
        if splash is not None:
            splash.finish(window)

    QTimer.singleShot(150 if launch_options.suppress_splash else 650, show_main_window)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
