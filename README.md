# Downloads Cleanup Assistant

A modern desktop utility for organizing and cleaning your Downloads folder.

Downloads Cleanup Assistant helps users scan a Downloads folder or selected directory, find duplicate files, review large downloads, locate old unused files, and recover wasted storage safely. The app uses a clean modern green interface with dashboard analytics, search and filters, progress indicators, cleanup recommendations, exportable reports, saved preferences, and light/dark mode.

## Features

- Scan the Downloads folder or any selected directory
- Duplicate detection using file hashing
- Duplicate grouping with estimated recoverable storage
- One-click duplicate cleanup while keeping the oldest copy
- Large file analysis with configurable size thresholds
- Old file discovery with configurable age thresholds
- Modern dashboard with storage statistics
- Cleanup recommendations prioritized by potential savings
- Safe cleanup through the system Recycle Bin or Trash
- Search, sorting, multi-select, and quick filters
- File type, size, age, and cleanup-status filters
- Exportable cleanup reports and CSV inventories
- Green light and dark mode
- Remembered last folder and saved user preferences
- Progress indicators and background scanning
- Friendly empty states and validation messages

## Author

Isaac Gazula

## Installation

1. Install Python 3.11 or newer.
2. Install the dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the application:

```powershell
python main.py
```

If you prefer a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

You can also use the included launcher:

```powershell
.\run_downloads_cleanup_assistant.bat
```

## Usage

1. Open the application.
2. Click `Scan Downloads` to analyze your default Downloads folder.
3. Use `Select Folder` to scan another directory.
4. Review the dashboard cards for total files, storage usage, duplicates, large files, old files, and recoverable space.
5. Choose a tab for the results you want to inspect.
6. Search, sort, filter, and select files for cleanup.
7. Click `Clean Selected` or `Clean Duplicate Copies` to move files safely to the Recycle Bin or Trash.
8. Use `Export Report` to save a scan summary and CSV inventory.

## Project Architecture

- `main.py` starts the PyQt6 application.
- `downloads_cleanup_assistant/ui/main_window.py` builds the main dashboard interface, toolbar, theme toggle, settings dialog, scan flow, cleanup actions, reports, and footer branding.
- `downloads_cleanup_assistant/ui/widgets.py` contains reusable dashboard cards, recommendation cards, file table models, selection helpers, and search/filter proxies.
- `downloads_cleanup_assistant/ui/workers.py` runs scans in the background so the interface stays responsive.
- `downloads_cleanup_assistant/ui/theme.py` defines the green light and dark mode styles.
- `downloads_cleanup_assistant/core/models.py` contains typed scan result, file record, duplicate group, recommendation, and settings models.
- `downloads_cleanup_assistant/core/scanner.py` scans folders, hashes duplicate candidates, groups duplicates, detects large and old files, and generates recommendations.
- `downloads_cleanup_assistant/core/cleanup.py` moves files safely to the OS Recycle Bin or Trash, with a local recovery fallback when needed.
- `downloads_cleanup_assistant/core/reporting.py` exports text scan summaries and CSV inventories.
- `downloads_cleanup_assistant/core/preferences.py` saves theme, thresholds, and the last scanned folder.
- `downloads_cleanup_assistant/core/utils.py` contains file categorization and storage formatting helpers.

## Cleanup Notes

Downloads Cleanup Assistant never permanently deletes files. Cleanup actions use the system Recycle Bin or Trash when available. If the platform trash mechanism is unavailable, the app moves files into a local recovery folder in the user's home directory as a safety fallback.

## Future Upgrades

- Packaged Windows installer
- File preview panel
- Duplicate group comparison view
- Storage trend history
- Scheduled scans
- Custom ignore folders
- Installer and archive cleanup presets
- Screenshot and temporary-file cleanup presets
- Export reports as PDF
- Per-folder cleanup rules

## Branding

Application: Downloads Cleanup Assistant  
Created by: Isaac Gazula  
Version: 1.0

© Downloads Cleanup Assistant. All Rights Reserved.
