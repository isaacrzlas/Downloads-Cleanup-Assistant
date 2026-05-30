"""Folder scanning and cleanup recommendation engine."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Callable

from .models import DuplicateGroup, FileRecord, Recommendation, ScanResult, ScanSettings
from .utils import file_category

ProgressCallback = Callable[[int, str], None]


class FolderScanner:
    """Analyze folders for duplicates, large files, old files, and cleanup wins."""

    def __init__(self, settings: ScanSettings) -> None:
        self.settings = settings

    def scan(self, folder: Path, progress: ProgressCallback | None = None) -> ScanResult:
        """Scan a folder recursively and return a complete analysis result."""

        folder = folder.expanduser().resolve()
        files = [path for path in folder.rglob("*") if path.is_file()]
        total = max(len(files), 1)
        now = datetime.now()
        records: list[FileRecord] = []

        for index, path in enumerate(files, start=1):
            if progress:
                progress(round(index / total * 40), f"Reading {path.name}")
            try:
                stat = path.stat()
            except OSError:
                continue
            modified_at = datetime.fromtimestamp(stat.st_mtime)
            age_days = max(0, (now - modified_at).days)
            size = stat.st_size
            records.append(
                FileRecord(
                    path=path,
                    name=path.name,
                    extension=path.suffix.lower() or "(none)",
                    size=size,
                    modified_at=modified_at,
                    age_days=age_days,
                    category=file_category(path),
                    is_large=size >= self.settings.large_file_mb * 1024 * 1024,
                    is_old=age_days >= self.settings.old_file_days,
                )
            )

        duplicate_groups = self._find_duplicates(records, progress)
        large_files = sorted((record for record in records if record.is_large), key=lambda item: item.size, reverse=True)
        old_files = sorted((record for record in records if record.is_old), key=lambda item: item.age_days, reverse=True)
        total_size = sum(record.size for record in records)
        recoverable_size = sum(group.recoverable_size for group in duplicate_groups)
        recommendations = self._recommendations(duplicate_groups, large_files, old_files)
        recoverable_size = max(recoverable_size, sum(item.potential_savings for item in recommendations[:1]))

        if progress:
            progress(100, "Scan complete")

        return ScanResult(
            folder=folder,
            scanned_at=now,
            files=sorted(records, key=lambda item: item.size, reverse=True),
            duplicate_groups=duplicate_groups,
            large_files=large_files,
            old_files=old_files,
            recommendations=recommendations,
            total_size=total_size,
            recoverable_size=recoverable_size,
        )

    def _find_duplicates(
        self,
        records: list[FileRecord],
        progress: ProgressCallback | None,
    ) -> list[DuplicateGroup]:
        """Hash only same-size files to identify true duplicates efficiently."""

        by_size: dict[int, list[FileRecord]] = defaultdict(list)
        for record in records:
            by_size[record.size].append(record)

        candidates = [record for group in by_size.values() if len(group) > 1 for record in group]
        total = max(len(candidates), 1)
        by_hash: dict[str, list[FileRecord]] = defaultdict(list)

        for index, record in enumerate(candidates, start=1):
            if progress:
                progress(40 + round(index / total * 45), f"Checking duplicates: {record.name}")
            digest = self._hash_file(record.path)
            if digest:
                record.file_hash = digest
                by_hash[digest].append(record)

        groups: list[DuplicateGroup] = []
        for group_index, (digest, files) in enumerate(by_hash.items(), start=1):
            if len(files) <= 1:
                continue
            files.sort(key=lambda item: (item.modified_at, str(item.path)))
            group_id = f"DUP-{group_index:03d}"
            for duplicate in files[1:]:
                duplicate.is_duplicate = True
                duplicate.duplicate_group = group_id
            files[0].duplicate_group = group_id
            groups.append(DuplicateGroup(group_id=group_id, files=files))

        return sorted(groups, key=lambda group: group.recoverable_size, reverse=True)

    def _hash_file(self, path: Path) -> str | None:
        """Return a SHA-256 hash for a readable file."""

        sha256 = hashlib.sha256()
        try:
            with path.open("rb") as file:
                for chunk in iter(lambda: file.read(1024 * 1024), b""):
                    sha256.update(chunk)
        except OSError:
            return None
        return sha256.hexdigest()

    def _recommendations(
        self,
        duplicate_groups: list[DuplicateGroup],
        large_files: list[FileRecord],
        old_files: list[FileRecord],
    ) -> list[Recommendation]:
        """Create prioritized cleanup cards from analysis output."""

        recommendations: list[Recommendation] = []
        duplicate_files = [file for group in duplicate_groups for file in group.files[1:]]
        duplicate_savings = sum(file.size for file in duplicate_files)
        if duplicate_files:
            recommendations.append(
                Recommendation(
                    title="Remove duplicate copies",
                    description="Keep the oldest copy in each duplicate group and move extra copies to the Recycle Bin.",
                    action="Clean duplicate copies",
                    potential_savings=duplicate_savings,
                    priority=1,
                    files=duplicate_files,
                )
            )

        top_large = large_files[:20]
        if top_large:
            recommendations.append(
                Recommendation(
                    title="Review large downloads",
                    description="These files use the most storage and are good candidates for archiving or cleanup.",
                    action="Review large files",
                    potential_savings=sum(file.size for file in top_large),
                    priority=2,
                    files=top_large,
                )
            )

        stale = [file for file in old_files if not file.is_duplicate][:50]
        if stale:
            recommendations.append(
                Recommendation(
                    title="Archive old downloads",
                    description="Older files often include forgotten installers, documents, and temporary exports.",
                    action="Review old files",
                    potential_savings=sum(file.size for file in stale),
                    priority=3,
                    files=stale,
                )
            )

        return sorted(recommendations, key=lambda item: (item.priority, -item.potential_savings))
