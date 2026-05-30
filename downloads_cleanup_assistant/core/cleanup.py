"""Safe cleanup helpers that avoid permanent deletion."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable

ProgressCallback = Callable[[int, str], None]


class SafeCleaner:
    """Move files to the OS trash or a local recovery folder as a last resort."""

    def clean(self, paths: list[Path], progress: ProgressCallback | None = None) -> tuple[int, list[str]]:
        """Move selected files away safely and return a count plus failures."""

        cleaned = 0
        errors: list[str] = []
        total = max(len(paths), 1)
        for index, path in enumerate(paths, start=1):
            if progress:
                progress(round((index - 1) / total * 100), f"Preparing cleanup: {path.name}")
            try:
                if not path.exists() or not path.is_file():
                    continue
                self._move_to_trash(path)
                cleaned += 1
            except Exception as exc:  # noqa: BLE001 - surfaced to the user as a cleanup failure.
                errors.append(f"{path}: {exc}")
            finally:
                if progress:
                    progress(round(index / total * 100), f"Cleaned {index} of {total} file(s)")
        return cleaned, errors

    def _move_to_trash(self, path: Path) -> None:
        """Use the best available system trash mechanism."""

        system = platform.system()
        try:
            from send2trash import send2trash  # type: ignore

            send2trash(str(path))
            return
        except ImportError:
            pass
        except Exception:
            if system not in {"Windows", "Darwin"} and not shutil.which("gio"):
                raise

        if system == "Windows":
            self._windows_recycle_bin(path)
            return
        if system == "Darwin":
            subprocess.run(["osascript", "-e", f'tell application "Finder" to delete POSIX file "{path}"'], check=True)
            return
        if shutil.which("gio"):
            subprocess.run(["gio", "trash", str(path)], check=True)
            return

        self._fallback_recovery_folder(path)

    def _windows_recycle_bin(self, path: Path) -> None:
        """Move a file to the Windows Recycle Bin through SHFileOperation."""

        import ctypes
        from ctypes import wintypes

        FO_DELETE = 3
        FOF_ALLOWUNDO = 0x40
        FOF_NOCONFIRMATION = 0x10
        FOF_SILENT = 0x04

        class SHFILEOPSTRUCTW(ctypes.Structure):
            _fields_ = [
                ("hwnd", wintypes.HWND),
                ("wFunc", wintypes.UINT),
                ("pFrom", wintypes.LPCWSTR),
                ("pTo", wintypes.LPCWSTR),
                ("fFlags", wintypes.UINT),
                ("fAnyOperationsAborted", wintypes.BOOL),
                ("hNameMappings", wintypes.LPVOID),
                ("lpszProgressTitle", wintypes.LPCWSTR),
            ]

        operation = SHFILEOPSTRUCTW()
        operation.wFunc = FO_DELETE
        operation.pFrom = str(path) + "\0\0"
        operation.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
        result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(operation))
        if result != 0:
            raise OSError(f"Recycle Bin operation failed with code {result}")

    def _fallback_recovery_folder(self, path: Path) -> None:
        """Last-resort safety net when the platform trash is unavailable."""

        recovery_folder = Path.home() / ".DownloadsCleanupAssistantTrash" / time.strftime("%Y%m%d-%H%M%S")
        recovery_folder.mkdir(parents=True, exist_ok=True)
        target = recovery_folder / path.name
        counter = 1
        while target.exists():
            target = recovery_folder / f"{path.stem}-{counter}{path.suffix}"
            counter += 1
        os.replace(path, target)
