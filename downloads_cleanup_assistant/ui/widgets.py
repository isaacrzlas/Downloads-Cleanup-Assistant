"""Reusable UI widgets and table models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QObject, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from downloads_cleanup_assistant.core.models import FileRecord, Recommendation
from downloads_cleanup_assistant.core.utils import human_size


class StatCard(QFrame):
    """A compact analytics card used by the dashboard."""

    def __init__(self, icon: str, title: str, description: str) -> None:
        super().__init__()
        self.setObjectName("StatCard")
        self.setMinimumHeight(128)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(5)

        header = QHBoxLayout()
        self.icon_label = QLabel(icon)
        self.icon_label.setFixedWidth(28)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: 750;")
        header.addWidget(self.icon_label)
        header.addWidget(self.title_label)
        header.addStretch()

        self.value_label = QLabel("0")
        self.value_label.setObjectName("StatValue")
        self.description_label = QLabel(description)
        self.description_label.setObjectName("Muted")
        self.description_label.setWordWrap(True)

        layout.addLayout(header)
        layout.addWidget(self.value_label)
        layout.addWidget(self.description_label)

    def set_value(self, value: str) -> None:
        """Update the card's main number."""

        self.value_label.setText(value)


class RecommendationCard(QFrame):
    """A dashboard card for one cleanup recommendation."""

    def __init__(self, recommendation: Recommendation) -> None:
        super().__init__()
        self.setObjectName("RecommendationCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(16)
        left = QVBoxLayout()
        title = QLabel(recommendation.title)
        title.setStyleSheet("font-size: 12pt; font-weight: 800;")
        description = QLabel(recommendation.description)
        description.setObjectName("Muted")
        description.setWordWrap(True)
        left.addWidget(title)
        left.addWidget(description)
        savings = QLabel(human_size(recommendation.potential_savings))
        savings.setObjectName("StatValue")
        savings.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(left, 1)
        layout.addWidget(savings)


class FileTableModel(QAbstractTableModel):
    """Table model with typed sorting values for scanned files."""

    headers = ["Name", "Category", "Size", "Age", "Modified", "Status", "Path"]

    def __init__(self, records: list[FileRecord] | None = None) -> None:
        super().__init__()
        self.records = records or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.records)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        record = self.records[index.row()]
        column = index.column()
        values = [
            record.name,
            record.category,
            human_size(record.size),
            f"{record.age_days} days",
            record.modified_at.strftime("%Y-%m-%d %H:%M"),
            self._status(record),
            str(record.path),
        ]
        sort_values = [
            record.name.lower(),
            record.category,
            record.size,
            record.age_days,
            record.modified_at.timestamp(),
            self._status(record),
            str(record.path).lower(),
        ]
        if role == Qt.ItemDataRole.DisplayRole:
            return values[column]
        if role == Qt.ItemDataRole.UserRole:
            return sort_values[column]
        if role == Qt.ItemDataRole.ToolTipRole:
            return str(record.path)
        if role == Qt.ItemDataRole.ForegroundRole and record.is_duplicate:
            return QColor("#168f55")
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None

    def set_records(self, records: list[FileRecord]) -> None:
        """Replace table data."""

        self.beginResetModel()
        self.records = records
        self.endResetModel()

    def record_at(self, row: int) -> FileRecord | None:
        """Return the file record at a model row."""

        if 0 <= row < len(self.records):
            return self.records[row]
        return None

    def _status(self, record: FileRecord) -> str:
        statuses: list[str] = []
        if record.is_duplicate:
            statuses.append("Duplicate")
        if record.is_large:
            statuses.append("Large")
        if record.is_old:
            statuses.append("Old")
        return ", ".join(statuses) if statuses else "Normal"


class FileFilterProxy(QSortFilterProxyModel):
    """Search and filter scanned files by category and cleanup status."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.search_text = ""
        self.category = "All"
        self.status = "All"
        self.min_size_mb = 0
        self.min_age_days = 0
        self.setSortRole(Qt.ItemDataRole.UserRole)

    def set_search(self, text: str) -> None:
        self.search_text = text.lower().strip()
        self.invalidateFilter()

    def set_category(self, category: str) -> None:
        self.category = category
        self.invalidateFilter()

    def set_status(self, status: str) -> None:
        self.status = status
        self.invalidateFilter()

    def set_min_size_mb(self, value: int) -> None:
        self.min_size_mb = value
        self.invalidateFilter()

    def set_min_age_days(self, value: int) -> None:
        self.min_age_days = value
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        if not isinstance(model, FileTableModel):
            return True
        record = model.record_at(source_row)
        if not record:
            return False
        searchable = f"{record.name} {record.category} {record.extension} {record.path}".lower()
        if self.search_text and self.search_text not in searchable:
            return False
        if self.category != "All" and record.category != self.category:
            return False
        if self.status == "Duplicates" and not record.is_duplicate:
            return False
        if self.status == "Large" and not record.is_large:
            return False
        if self.status == "Old" and not record.is_old:
            return False
        if self.min_size_mb and record.size < self.min_size_mb * 1024 * 1024:
            return False
        if self.min_age_days and record.age_days < self.min_age_days:
            return False
        return True


def selected_records(table, proxy: FileFilterProxy) -> list[FileRecord]:
    """Return selected file records from a table view."""

    records: list[FileRecord] = []
    model = proxy.sourceModel()
    if not isinstance(model, FileTableModel):
        return records
    for proxy_index in table.selectionModel().selectedRows():
        source_index = proxy.mapToSource(proxy_index)
        record = model.record_at(source_index.row())
        if record:
            records.append(record)
    return records


def path_list(records: list[FileRecord]) -> list[Path]:
    """Extract paths from file records."""

    return [record.path for record in records]
