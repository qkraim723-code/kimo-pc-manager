# Changelog

All notable changes to **Kimo PC Manager** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-19

### Added
- **Overview Dashboard**:
  - Visual layout inspired by modern mobile file managers.
  - Real-time CPU, RAM, and Disk space monitoring.
  - Live system drive usage bar with percentage and capacity details.
  - Quick action shortcuts to Photos, Videos, Documents, Downloads, Audio, Tools, and Duplicates.
- **Integrated File Manager**:
  - Full drive and directory navigation with breadcrumbs, forward/back history.
  - Categories filtering: Photos, Videos, Audio, Documents, Archives, Large Files (>100MB), and Recent.
  - Standard file operations: Create Folder, Rename, Copy, Move, and Delete to Recycle Bin via `send2trash`.
  - Conflict resolution dialogs (Rename, Overwrite, Skip).
  - File properties viewer and context menu actions.
- **Storage Analyzer**:
  - Deep recursive directory and disk scan in background thread.
  - Top folders consuming space and top largest files breakdown.
  - Safe error handling for symlinks, loops, and restricted permissions.
- **Safe Cleanup Center**:
  - Conservative review of supported temporary files and caches before cleanup.
  - Safety checks to avoid protected Windows system locations and skip files that are locked or in use.
  - Automatic skip of currently locked or in-use files.
  - Explicit confirmation modal before any deletion.
  - Direct integration with Windows Recycle Bin.
- **Device Performance**:
  - Real hardware telemetry (CPU %, RAM used/total, Disk I/O throughput read/write).
  - Machine specs: OS release, CPU cores, boot time, uptime.
  - Top active processes monitor with guarded process termination.
- **Duplicate File Finder**:
  - High-performance two-pass duplicate detection (exact size match -> chunked SHA-256 content hashing).
  - Group view with potential space reclaimed calculation.
  - Automatic duplicate selector with strict protection of original copies.
- **Windows Utilities**:
  - Quick launch shortcuts for Task Manager, Storage Sense, System Info, Disk Optimization, Disk Cleanup, Device Manager, and Resource Monitor.
- **Full Localization (Arabic & English)**:
  - Default English interface with Left-to-Right (LTR) layout.
  - Arabic interface with Right-to-Left (RTL) layout.
  - Dynamic in-app language switching with persistent settings.
- **Testing & Packaging**:
  - 17 automated tests covering core file, storage, and system services.
  - Windows standalone launcher (`run.bat`) and executable build script (`build.bat`).
  - Packaged Windows executable requests administrator approval through the Windows UAC prompt.
  - GitHub Actions automated CI workflow.
