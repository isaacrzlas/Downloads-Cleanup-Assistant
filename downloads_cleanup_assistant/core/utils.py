"""Formatting and categorization helpers."""

from __future__ import annotations

from pathlib import Path


CATEGORY_MAP: dict[str, tuple[str, ...]] = {
    "Documents": (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv"),
    "Images": (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".heic"),
    "Videos": (".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv"),
    "Audio": (".mp3", ".wav", ".aac", ".flac", ".m4a", ".ogg"),
    "Archives": (".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"),
    "Installers": (".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".appimage"),
    "Code": (".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".xml", ".sql"),
}


def file_category(path: Path) -> str:
    """Return a friendly category for a path extension."""

    extension = path.suffix.lower()
    for category, extensions in CATEGORY_MAP.items():
        if extension in extensions:
            return category
    return "Other"


def human_size(size: int) -> str:
    """Format bytes as a compact storage value."""

    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} TB"


def safe_percent(part: int, whole: int) -> int:
    """Return a rounded percentage without division errors."""

    if whole <= 0:
        return 0
    return round((part / whole) * 100)
