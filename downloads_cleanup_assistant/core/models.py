"""Typed data models shared by the cleanup engine and UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class FileRecord:
    """A scanned file and the metadata used for cleanup decisions."""

    path: Path
    name: str
    extension: str
    size: int
    modified_at: datetime
    age_days: int
    category: str
    file_hash: str | None = None
    duplicate_group: str | None = None
    is_duplicate: bool = False
    is_large: bool = False
    is_old: bool = False


@dataclass(slots=True)
class DuplicateGroup:
    """A group of files that share identical content."""

    group_id: str
    files: list[FileRecord]

    @property
    def recoverable_size(self) -> int:
        if len(self.files) <= 1:
            return 0
        return sum(file.size for file in self.files[1:])


@dataclass(slots=True)
class Recommendation:
    """A user-facing cleanup suggestion."""

    title: str
    description: str
    action: str
    potential_savings: int
    priority: int
    files: list[FileRecord] = field(default_factory=list)


@dataclass(slots=True)
class ScanSettings:
    """Settings that control cleanup analysis."""

    large_file_mb: int = 100
    old_file_days: int = 90


@dataclass(slots=True)
class ScanResult:
    """Complete output from a folder scan."""

    folder: Path
    scanned_at: datetime
    files: list[FileRecord]
    duplicate_groups: list[DuplicateGroup]
    large_files: list[FileRecord]
    old_files: list[FileRecord]
    recommendations: list[Recommendation]
    total_size: int
    recoverable_size: int

    @property
    def duplicate_files_count(self) -> int:
        return sum(max(0, len(group.files) - 1) for group in self.duplicate_groups)
