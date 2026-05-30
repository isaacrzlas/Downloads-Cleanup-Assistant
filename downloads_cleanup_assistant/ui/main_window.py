"""Main window for the Downloads Cleanup Assistant desktop application."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QThread, Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from downloads_cleanup_assistant import __app_name__, __author__, __version__
from downloads_cleanup_assistant.core.models import ScanResult, ScanSettings
from downloads_cleanup_assistant.core.preferences import Preferences
from downloads_cleanup_assistant.core.reporting import ReportExporter
from downloads_cleanup_assistant.core.utils import CATEGORY_MAP, human_size
from downloads_cleanup_assistant.ui.theme import DARK_STYLE, LIGHT_STYLE
from downloads_cleanup_assistant.ui.widgets import (
    FileFilterProxy,
    FileTableModel,
    RecommendationCard,
    StatCard,
    path_list,
    selected_records,
)
from downloads_cleanup_assistant.ui.workers import CleanupWorker, ScanWorker


class SettingsDialog(QDialog):
    """Edit analysis thresholds."""

    def __init__(self, settings: ScanSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.large_spin = QSpinBox()
        self.large_spin.setRange(1, 102400)
        self.large_spin.setValue(settings.large_file_mb)
        self.large_spin.setSuffix(" MB")
        self.old_spin = QSpinBox()
        self.old_spin.setRange(1, 3650)
        self.old_spin.setValue(settings.old_file_days)
        self.old_spin.setSuffix(" days")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        title = QLabel("Cleanup Thresholds")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        layout.addWidget(QLabel("Large files are files at or above:"))
        layout.addWidget(self.large_spin)
        layout.addWidget(QLabel("Old files are files older than:"))
        layout.addWidget(self.old_spin)

        buttons = QHBoxLayout()
        cancel = QPushButton("Cancel")
        save = QPushButton("Save")
        save.setObjectName("PrimaryButton")
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)
        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def settings(self) -> ScanSettings:
        """Return the edited settings."""

        return ScanSettings(self.large_spin.value(), self.old_spin.value())


class MainWindow(QMainWindow):
    """Commercial-style dashboard for download cleanup workflows."""

    def __init__(self) -> None:
        super().__init__()
        self.preferences = Preferences()
        self.result: ScanResult | None = None
        self.scan_thread: QThread | None = None
        self.scan_worker: ScanWorker | None = None
        self.cleanup_thread: QThread | None = None
        self.cleanup_worker: CleanupWorker | None = None
        self.pending_rescan_folder: Path | None = None
        self.reporter = ReportExporter()

        self.setWindowTitle(__app_name__)
        self.resize(1280, 820)
        self._build_ui()
        self._apply_theme()
        self._show_welcome()

    def _build_ui(self) -> None:
        """Assemble the main window layout."""

        root = QWidget()
        root.setObjectName("AppRoot")
        main = QVBoxLayout(root)
        main.setContentsMargins(16, 16, 16, 12)
        main.setSpacing(14)

        self.header = self._header()
        main.addWidget(self.header)

        self.stack = QStackedWidget()
        self.welcome_panel = self._welcome_panel()
        self.dashboard = self._dashboard_panel()
        self.stack.addWidget(self.welcome_panel)
        self.stack.addWidget(self.dashboard)
        main.addWidget(self.stack, 1)

        footer = QFrame()
        footer.setObjectName("Footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(14, 8, 14, 8)
        footer_layout.addWidget(QLabel("Made by Isaac Gazula"))
        footer_layout.addStretch()
        footer_layout.addWidget(QLabel("© Downloads Cleanup Assistant. All Rights Reserved."))
        main.addWidget(footer)

        self.setCentralWidget(root)

    def _header(self) -> QFrame:
        """Create the top command header."""

        frame = QFrame()
        frame.setObjectName("Header")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        title_block = QVBoxLayout()
        title = QLabel(__app_name__)
        title.setObjectName("AppTitle")
        subtitle = QLabel("Professional file cleanup and storage optimization")
        subtitle.setObjectName("Muted")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        layout.addLayout(title_block, 1)

        self.scan_button = QPushButton("Scan Downloads")
        self.scan_button.setObjectName("PrimaryButton")
        self.scan_button.setToolTip("Scan the default Downloads folder.")
        self.scan_button.clicked.connect(self._scan_downloads)
        self.select_button = QPushButton("Select Folder")
        self.select_button.setToolTip("Choose any folder to analyze.")
        self.select_button.clicked.connect(self._select_folder)
        self.theme_button = QPushButton("Dark Mode" if self.preferences.theme == "light" else "Light Mode")
        self.theme_button.setToolTip("Switch between light and dark mode.")
        self.theme_button.clicked.connect(self._toggle_theme)
        self.settings_button = QPushButton("Settings")
        self.settings_button.setToolTip("Configure large-file and old-file thresholds.")
        self.settings_button.clicked.connect(self._open_settings)
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.setToolTip("Open the scanned folder in File Explorer.")
        self.open_folder_button.setEnabled(False)
        self.open_folder_button.clicked.connect(self._open_current_folder)

        for button in (self.scan_button, self.select_button, self.open_folder_button, self.theme_button, self.settings_button):
            layout.addWidget(button)
        return frame

    def _welcome_panel(self) -> QWidget:
        """Create first-launch onboarding."""

        wrapper = QWidget()
        wrapper.setObjectName("StackPage")
        outer = QVBoxLayout(wrapper)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch()
        panel = QFrame()
        panel.setObjectName("WelcomePanel")
        panel.setMinimumWidth(620)
        panel.setMaximumWidth(700)
        panel.setMinimumHeight(430)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(38, 34, 38, 34)
        layout.setSpacing(18)
        title = QLabel("Welcome to Downloads Cleanup Assistant")
        title.setObjectName("SectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description = QLabel("This tool helps you find duplicate files, recover disk space, locate old downloads, identify large files, and clean safely.")
        description.setObjectName("Muted")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        start = QPushButton("Start Scan")
        start.setObjectName("PrimaryButton")
        start.setToolTip("Begin by scanning your Downloads folder.")
        start.clicked.connect(self._scan_downloads)
        bullets = QFrame()
        bullets.setObjectName("WelcomeBullets")
        bullets_layout = QVBoxLayout(bullets)
        bullets_layout.setContentsMargins(24, 18, 24, 18)
        bullets_layout.setSpacing(8)
        for text in (
            "✓ Find duplicate files",
            "✓ Recover disk space",
            "✓ Locate old downloads",
            "✓ Identify large files",
            "✓ Safely clean your computer",
        ):
            row = QLabel(text)
            row.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.setMinimumHeight(24)
            bullets_layout.addWidget(row)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(bullets)
        layout.addStretch()
        layout.addWidget(start, alignment=Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(panel, alignment=Qt.AlignmentFlag.AlignCenter)
        outer.addStretch()
        return wrapper

    def _dashboard_panel(self) -> QWidget:
        """Create analytics cards, tabs, and progress UI."""

        wrapper = QWidget()
        wrapper.setObjectName("StackPage")
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)

        card_grid = QGridLayout()
        card_grid.setSpacing(12)
        self.cards = {
            "files": StatCard("F", "Total Files", "Files discovered in the selected folder."),
            "storage": StatCard("S", "Storage Used", "Total storage used by scanned files."),
            "duplicates": StatCard("D", "Duplicate Files", "Extra copies that can be cleaned safely."),
            "large": StatCard("L", "Large Files", "Files above the configured size threshold."),
            "old": StatCard("O", "Old Files", "Files older than the configured age threshold."),
            "recoverable": StatCard("R", "Recoverable Space", "Estimated storage that can be reviewed or recovered."),
        }
        for index, card in enumerate(self.cards.values()):
            card_grid.addWidget(card, index // 3, index % 3)
        layout.addLayout(card_grid)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._overview_tab(), "Overview")
        self.tabs.addTab(self._table_tab("duplicates"), "Duplicates")
        self.tabs.addTab(self._table_tab("large"), "Large Files")
        self.tabs.addTab(self._table_tab("old"), "Old Files")
        self.tabs.addTab(self._recommendations_tab(), "Recommendations")
        layout.addWidget(self.tabs, 1)
        return wrapper

    def _overview_tab(self) -> QWidget:
        """Create an all-files inventory tab."""

        self.overview_table, self.overview_model, self.overview_proxy = self._create_file_table()
        return self._table_page(
            "Overview",
            "Browse every scanned file, search instantly, and filter by type or cleanup status.",
            self.overview_table,
            self.overview_proxy,
        )

    def _table_tab(self, name: str) -> QWidget:
        """Create a specialized results tab."""

        table, model, proxy = self._create_file_table()
        setattr(self, f"{name}_table", table)
        setattr(self, f"{name}_model", model)
        setattr(self, f"{name}_proxy", proxy)
        titles = {
            "duplicates": ("Duplicate Files", "Extra copies are grouped by matching file hash. The oldest copy is preserved by default."),
            "large": ("Large Files", "Review files exceeding the current size threshold."),
            "old": ("Old Files", "Find forgotten downloads based on file age."),
        }
        title, description = titles[name]
        return self._table_page(title, description, table, proxy)

    def _recommendations_tab(self) -> QWidget:
        """Create cleanup recommendations and export controls."""

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        header = QHBoxLayout()
        text = QVBoxLayout()
        title = QLabel("Recommendations")
        title.setObjectName("SectionTitle")
        description = QLabel("Prioritized cleanup suggestions based on duplicate, large, and old-file analysis.")
        description.setObjectName("Muted")
        description.setWordWrap(True)
        text.addWidget(title)
        text.addWidget(description)
        export = QPushButton("Export Report")
        export.setToolTip("Save a text summary and optional CSV inventory.")
        export.clicked.connect(self._export_report)
        clean_duplicates = QPushButton("Clean Duplicate Copies")
        clean_duplicates.setObjectName("PrimaryButton")
        clean_duplicates.setToolTip("Move extra duplicate copies to the Recycle Bin while preserving the oldest copy.")
        clean_duplicates.clicked.connect(self._clean_duplicate_copies)
        header.addLayout(text, 1)
        header.addWidget(clean_duplicates)
        header.addWidget(export)
        layout.addLayout(header)

        self.recommendations_container = QVBoxLayout()
        layout.addLayout(self.recommendations_container)
        layout.addStretch()
        return page

    def _create_file_table(self) -> tuple[QTableView, FileTableModel, FileFilterProxy]:
        """Create a sortable, multi-select table."""

        model = FileTableModel()
        proxy = FileFilterProxy(self)
        proxy.setSourceModel(model)
        table = QTableView()
        table.setModel(proxy)
        table.setSortingEnabled(True)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in range(1, 6):
            table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        table.sortByColumn(2, Qt.SortOrder.DescendingOrder)
        return table, model, proxy

    def _table_page(
        self,
        title_text: str,
        description_text: str,
        table: QTableView,
        proxy: FileFilterProxy,
    ) -> QWidget:
        """Wrap a table with search, filters, and cleanup actions."""

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel(title_text)
        title.setObjectName("SectionTitle")
        description = QLabel(description_text)
        description.setObjectName("Muted")
        description.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(description)

        controls = QHBoxLayout()
        search = QLineEdit()
        search.setPlaceholderText("Search files")
        search.setToolTip("Search by filename, category, extension, or path.")
        search.textChanged.connect(proxy.set_search)
        category = QComboBox()
        category.setToolTip("Filter by file type.")
        category.addItems(["All", *CATEGORY_MAP.keys(), "Other"])
        category.currentTextChanged.connect(proxy.set_category)
        status = QComboBox()
        status.setToolTip("Filter by cleanup status.")
        status.addItems(["All", "Duplicates", "Large", "Old"])
        status.currentTextChanged.connect(proxy.set_status)
        min_size = QSpinBox()
        min_size.setRange(0, 102400)
        min_size.setSuffix(" MB")
        min_size.setToolTip("Show only files at or above this size. Use 0 to disable.")
        min_size.valueChanged.connect(proxy.set_min_size_mb)
        min_age = QSpinBox()
        min_age.setRange(0, 3650)
        min_age.setSuffix(" days")
        min_age.setToolTip("Show only files at or above this age. Use 0 to disable.")
        min_age.valueChanged.connect(proxy.set_min_age_days)
        select_all = QPushButton("Select All")
        select_all.setToolTip("Select all visible rows.")
        select_all.clicked.connect(table.selectAll)
        clear_selection = QPushButton("Clear Selection")
        clear_selection.setToolTip("Clear selected rows.")
        clear_selection.clicked.connect(table.clearSelection)
        clean = QPushButton("Clean Selected")
        clean.setObjectName("DangerButton")
        clean.setToolTip("Move selected files to the Recycle Bin or Trash.")
        clean.clicked.connect(lambda: self._clean_selected(table, proxy))

        for widget in (search, category, status, min_size, min_age, select_all, clear_selection, clean):
            controls.addWidget(widget)
        layout.addLayout(controls)

        empty = QLabel("Scan a folder to begin analysis.")
        empty.setObjectName("Muted")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(table, 1)
        layout.addWidget(empty)
        table.model().rowsInserted.connect(lambda: empty.setVisible(proxy.rowCount() == 0))
        table.model().modelReset.connect(lambda: empty.setVisible(proxy.rowCount() == 0))
        return page

    def _scan_downloads(self) -> None:
        """Scan the user's Downloads folder."""

        folder = Path.home() / "Downloads"
        if not folder.exists():
            folder = Path(self.preferences.last_folder)
        self._start_scan(folder)

    def _select_folder(self) -> None:
        """Let the user choose a folder to scan."""

        folder = QFileDialog.getExistingDirectory(self, "Select folder to scan", self.preferences.last_folder)
        if folder:
            self._start_scan(Path(folder))

    def _start_scan(self, folder: Path) -> None:
        """Start a background scan."""

        if self._is_busy():
            return
        if not folder.exists():
            QMessageBox.warning(self, "Folder not found", f"The folder could not be found:\n{folder}")
            return

        self.stack.setCurrentWidget(self.dashboard)
        self._begin_progress("Preparing scan...")

        self.scan_thread = QThread(self)
        self.scan_worker = ScanWorker(folder, self.preferences.settings)
        self.scan_worker.moveToThread(self.scan_thread)
        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.progress.connect(self._scan_progress)
        self.scan_worker.finished.connect(self._scan_finished)
        self.scan_worker.failed.connect(self._scan_failed)
        self.scan_worker.finished.connect(self.scan_thread.quit)
        self.scan_worker.failed.connect(self.scan_thread.quit)
        self.scan_thread.finished.connect(self.scan_worker.deleteLater)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)
        self.scan_thread.start()

    def _scan_progress(self, value: int, message: str) -> None:
        """Update progress from the worker."""

        self.progress.setValue(value)
        self.progress.setFormat(message)

    def _scan_finished(self, result: ScanResult) -> None:
        """Populate the UI after a scan completes."""

        self.result = result
        self.preferences.last_folder = str(result.folder)
        self.preferences.save()
        self.scan_button.setEnabled(True)
        self.select_button.setEnabled(True)
        self.open_folder_button.setEnabled(True)
        self.progress.setValue(100)
        self.progress.setFormat("Scan complete")
        self._set_controls_enabled(True)
        self._update_dashboard(result)
        self._show_welcome(False)

    def _scan_failed(self, message: str) -> None:
        """Restore the UI and report scan failures."""

        self._set_controls_enabled(True)
        self.progress.setVisible(False)
        QMessageBox.critical(self, "Scan failed", message)

    def _show_welcome(self, visible: bool = True) -> None:
        """Switch between onboarding and dashboard."""

        self.stack.setCurrentWidget(self.welcome_panel if visible else self.dashboard)

    def _update_dashboard(self, result: ScanResult) -> None:
        """Refresh stats, tables, and recommendation cards."""

        self.cards["files"].set_value(str(len(result.files)))
        self.cards["storage"].set_value(human_size(result.total_size))
        self.cards["duplicates"].set_value(str(result.duplicate_files_count))
        self.cards["large"].set_value(str(len(result.large_files)))
        self.cards["old"].set_value(str(len(result.old_files)))
        self.cards["recoverable"].set_value(human_size(result.recoverable_size))

        self.overview_model.set_records(result.files)
        self.duplicates_model.set_records([file for group in result.duplicate_groups for file in group.files])
        self.large_model.set_records(result.large_files)
        self.old_model.set_records(result.old_files)

        self._clear_layout(self.recommendations_container)
        if result.recommendations:
            for recommendation in result.recommendations:
                self.recommendations_container.addWidget(RecommendationCard(recommendation))
        else:
            empty = QLabel("No cleanup recommendations were found.")
            empty.setObjectName("Muted")
            self.recommendations_container.addWidget(empty)

    def _clean_selected(self, table: QTableView, proxy: FileFilterProxy) -> None:
        """Confirm and safely clean selected files."""

        records = selected_records(table, proxy)
        if not records:
            QMessageBox.information(self, "No files selected", "Select one or more files before cleanup.")
            return
        savings = human_size(sum(record.size for record in records))
        answer = QMessageBox.question(
            self,
            "Clean selected files?",
            f"Move {len(records)} selected file(s) to the Recycle Bin or Trash?\n\nEstimated space: {savings}",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._start_cleanup(path_list(records), self.result.folder if self.result else None)

    def _clean_duplicate_copies(self) -> None:
        """Clean only duplicate copies, preserving the first file in every group."""

        if not self.result or not self.result.duplicate_groups:
            QMessageBox.information(self, "No duplicates", "No duplicate files were found in the latest scan.")
            return
        records = [file for group in self.result.duplicate_groups for file in group.files[1:]]
        savings = human_size(sum(record.size for record in records))
        answer = QMessageBox.question(
            self,
            "Clean duplicate copies?",
            f"Move {len(records)} duplicate copy file(s) to the Recycle Bin or Trash?\n\nThe oldest copy in each group will be kept.\nEstimated space: {savings}",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._start_cleanup(path_list(records), self.result.folder)

    def _start_cleanup(self, paths: list[Path], rescan_folder: Path | None) -> None:
        """Move files to trash in a worker thread so the UI stays responsive."""

        if self._is_busy():
            return
        self.pending_rescan_folder = rescan_folder
        self.stack.setCurrentWidget(self.dashboard)
        self._begin_progress(f"Cleaning {len(paths)} file(s)...")

        self.cleanup_thread = QThread(self)
        self.cleanup_worker = CleanupWorker(paths)
        self.cleanup_worker.moveToThread(self.cleanup_thread)
        self.cleanup_thread.started.connect(self.cleanup_worker.run)
        self.cleanup_worker.progress.connect(self._operation_progress)
        self.cleanup_worker.finished.connect(self._cleanup_finished)
        self.cleanup_worker.failed.connect(self._cleanup_failed)
        self.cleanup_worker.finished.connect(self.cleanup_thread.quit)
        self.cleanup_worker.failed.connect(self.cleanup_thread.quit)
        self.cleanup_thread.finished.connect(self.cleanup_worker.deleteLater)
        self.cleanup_thread.finished.connect(self._rescan_after_cleanup)
        self.cleanup_thread.finished.connect(self.cleanup_thread.deleteLater)
        self.cleanup_thread.start()

    def _cleanup_finished(self, cleaned: int, errors: list[str]) -> None:
        """Show cleanup results and rescan the folder."""

        self.progress.setValue(100)
        self.progress.setFormat("Cleanup complete")
        self._set_controls_enabled(True)
        if errors:
            QMessageBox.warning(self, "Cleanup completed with warnings", f"Cleaned {cleaned} file(s).\n\n" + "\n".join(errors[:8]))
        else:
            QMessageBox.information(self, "Cleanup complete", f"Cleaned {cleaned} file(s) safely.")

    def _cleanup_failed(self, message: str) -> None:
        """Restore the UI and report cleanup failures."""

        self._set_controls_enabled(True)
        self.progress.setVisible(False)
        self.pending_rescan_folder = None
        QMessageBox.critical(self, "Cleanup failed", message)

    def _rescan_after_cleanup(self) -> None:
        """Refresh scan results after the cleanup thread has fully stopped."""

        folder = self.pending_rescan_folder
        self.pending_rescan_folder = None
        if folder:
            self._start_scan(folder)

    def _open_current_folder(self) -> None:
        """Open the currently scanned folder."""

        if self.result:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.result.folder)))

    def _export_report(self) -> None:
        """Export a text summary and offer CSV inventory export."""

        if not self.result:
            QMessageBox.information(self, "No scan available", "Scan a folder before exporting a report.")
            return
        path_text, _ = QFileDialog.getSaveFileName(
            self,
            "Export cleanup report",
            str(Path.home() / "Downloads Cleanup Report.txt"),
            "Text report (*.txt)",
        )
        if not path_text:
            return
        path = Path(path_text)
        self.reporter.export_text_summary(self.result, path)
        csv_path = path.with_suffix(".csv")
        self.reporter.export_csv_inventory(self.result, csv_path)
        QMessageBox.information(self, "Report exported", f"Report saved to:\n{path}\n\nCSV inventory saved to:\n{csv_path}")

    def _open_settings(self) -> None:
        """Open threshold settings."""

        dialog = SettingsDialog(self.preferences.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.preferences.settings = dialog.settings()
            self.preferences.save()
            if self.result:
                self._start_scan(self.result.folder)

    def _toggle_theme(self) -> None:
        """Switch light and dark modes instantly."""

        self.preferences.theme = "dark" if self.preferences.theme == "light" else "light"
        self.preferences.save()
        self.theme_button.setText("Dark Mode" if self.preferences.theme == "light" else "Light Mode")
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Apply the current application stylesheet."""

        QApplication.instance().setStyleSheet(DARK_STYLE if self.preferences.theme == "dark" else LIGHT_STYLE)

    def _begin_progress(self, message: str) -> None:
        """Show progress for a long-running operation."""

        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat(message)
        self._set_controls_enabled(False)

    def _operation_progress(self, value: int, message: str) -> None:
        """Update the shared progress bar."""

        self.progress.setValue(value)
        self.progress.setFormat(message)

    def _set_controls_enabled(self, enabled: bool) -> None:
        """Enable or disable controls that can start work."""

        self.scan_button.setEnabled(enabled)
        self.select_button.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)
        self.open_folder_button.setEnabled(enabled and self.result is not None)

    def _is_busy(self) -> bool:
        """Return whether scan or cleanup work is active."""

        scan_running = self.scan_thread is not None and self.scan_thread.isRunning()
        cleanup_running = self.cleanup_thread is not None and self.cleanup_thread.isRunning()
        return scan_running or cleanup_running

    def _show_about(self) -> None:
        """Display branding and version information."""

        QMessageBox.about(
            self,
            f"About {__app_name__}",
            f"{__app_name__}\nVersion {__version__}\n\nCreated by {__author__}\n\n© Downloads Cleanup Assistant.\nAll Rights Reserved.\n\nProfessional file cleanup and storage optimization tool.",
        )

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        """Remove widgets from a layout before rebuilding it."""

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override.
        """Add a small convenience shortcut for opening the scanned folder."""

        if event.key() == Qt.Key.Key_O and event.modifiers() == Qt.KeyboardModifier.ControlModifier and self.result:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.result.folder)))
            return
        super().keyPressEvent(event)
