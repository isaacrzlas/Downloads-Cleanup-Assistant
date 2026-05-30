"""Background workers for long-running UI operations."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from downloads_cleanup_assistant.core.models import ScanResult, ScanSettings
from downloads_cleanup_assistant.core.scanner import FolderScanner
from downloads_cleanup_assistant.core.cleanup import SafeCleaner


class ScanWorker(QObject):
    """Run folder scans off the UI thread."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, folder: Path, settings: ScanSettings) -> None:
        super().__init__()
        self.folder = folder
        self.settings = settings

    @pyqtSlot()
    def run(self) -> None:
        """Execute the scan and emit the result."""

        try:
            scanner = FolderScanner(self.settings)
            result: ScanResult = scanner.scan(self.folder, self.progress.emit)
            self.finished.emit(result)
        except Exception as exc:  # noqa: BLE001 - shown in an error dialog.
            self.failed.emit(str(exc))


class CleanupWorker(QObject):
    """Move files to trash off the UI thread."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(int, list)
    failed = pyqtSignal(str)

    def __init__(self, paths: list[Path]) -> None:
        super().__init__()
        self.paths = paths

    @pyqtSlot()
    def run(self) -> None:
        """Execute safe cleanup and emit the result."""

        try:
            cleaner = SafeCleaner()
            cleaned, errors = cleaner.clean(self.paths, self.progress.emit)
            self.finished.emit(cleaned, errors)
        except Exception as exc:  # noqa: BLE001 - shown in an error dialog.
            self.failed.emit(str(exc))
