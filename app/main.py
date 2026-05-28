from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.core.logging_config import configure_logging
from app.core.paths import ensure_app_dirs
from app.ui.main_window import MainWindow


def _load_stylesheet() -> str:
    style_path = Path(__file__).parent / "resources" / "styles" / "app.qss"
    if not style_path.exists():
        return ""
    return style_path.read_text(encoding="utf-8")


def main() -> int:
    ensure_app_dirs()
    configure_logging()

    app = QApplication(sys.argv)
    stylesheet = _load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
