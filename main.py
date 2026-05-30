"""Application entry point for Downloads Cleanup Assistant."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from downloads_cleanup_assistant.ui.main_window import MainWindow


def log_uncaught_exception(exc_type, exc_value, exc_traceback) -> None:
    """Write unexpected GUI errors to a local crash log."""

    crash_log = Path(__file__).with_name("crash.log")
    message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    crash_log.write_text(message, encoding="utf-8")
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main() -> int:
    """Start the desktop application."""

    sys.excepthook = log_uncaught_exception
    app = QApplication(sys.argv)
    app.setApplicationName("Downloads Cleanup Assistant")
    app.setOrganizationName("Isaac Gazula")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
