"""Persisted user preferences for theme and thresholds."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import ScanSettings


class Preferences:
    """Load and save small application preferences as JSON."""

    def __init__(self) -> None:
        self.path = Path.home() / ".downloads_cleanup_assistant.json"
        self.theme = "light"
        self.last_folder = str(Path.home() / "Downloads")
        self.settings = ScanSettings()
        self.load()

    def load(self) -> None:
        """Load preferences when the file exists."""

        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        self.theme = data.get("theme", self.theme)
        self.last_folder = data.get("last_folder", self.last_folder)
        settings = data.get("settings", {})
        self.settings = ScanSettings(
            large_file_mb=int(settings.get("large_file_mb", self.settings.large_file_mb)),
            old_file_days=int(settings.get("old_file_days", self.settings.old_file_days)),
        )

    def save(self) -> None:
        """Write preferences to the user's profile."""

        payload = {
            "theme": self.theme,
            "last_folder": self.last_folder,
            "settings": asdict(self.settings),
        }
        try:
            self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            pass
