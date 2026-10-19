# Kimo PC Manager 💻🚀

**Kimo PC Manager** is a modern, transparent, and user-friendly desktop application for Windows 10 and Windows 11 (64-bit). Inspired by the intuitive clarity of mobile device managers, it brings together all essential tools—file management, storage analysis, hardware monitoring, safe temporary cleanup, duplicate file detection, and Windows native utilities—into a single, unified interface.

Built with **Python**, **PySide6 (Qt6)**, **psutil**, and **send2trash**.

---

## 🌟 Key Features

### 1. 📊 Overview Dashboard
- Visual layout based on modern dark green cards (`#17251F`, `#263830`, `#C7F36B`).
- Real-time hardware telemetry: CPU load, RAM usage, and System Drive capacity.
- Live system drive progress bar showing real bytes used, free, and total.
- Quick action shortcuts to Photos, Videos, Documents, Downloads, Audio, Windows Tools, and Duplicate Finder.

### 2. 📁 Integrated File Manager
- Seamless browsing across all internal and external drives.
- Path breadcrumbs with backward, forward, parent folder, and refresh actions.
- Category filters: **Photos, Videos, Audio, Documents, Compressed Archives, Large Files (>100 MB), and Recent Files**.
- Safe operations:
  - Create new folders.
  - Rename items.
  - Copy and Move items with automated conflict resolution (**Keep Both / Auto-Rename, Replace, Skip**).
  - Safe deletion using Windows Recycle Bin via `send2trash`.
  - Item properties inspector.
  - Double-click to open files with their default Windows programs or open in Windows Explorer.

### 3. 💾 Storage Analyzer
- Deep recursive scan of selected drives or custom folders in background threads.
- Identifies the directories consuming the most disk space.
- Displays the top largest files found.
- Resilient against restricted permissions, loops, and symbolic links without freezing the UI.

### 4. 🛡️ Safe Cleanup Center
- **Conservative & Non-Destructive**: Audits only safe temporary caches (%TEMP%, user browser cache, thumbnail previews).
- **Strict Guardrails**: Never touches System32, WinSxS, registry keys, active system logs, or drivers.
- **Safety First**: Automatically skips locked or currently in-use files.
- Full transparency: displays discovered files and estimated reclaimed space before asking for user confirmation.
- One-click access to the official Windows Recycle Bin.

### 5. ⚡ Device Performance Monitor
- Real-time CPU, RAM, and Disk I/O read/write throughput metrics.
- Machine hardware specifications (OS build, CPU cores, boot timestamp, uptime).
- Process monitor listing the top resource-heavy applications, with guarded process termination.

### 6. 📑 Duplicate File Finder
- High-efficiency two-pass duplicate detection:
  1. Compares exact byte sizes.
  2. Computes chunked SHA-256 hashes for size candidates.
- Categorized duplicate groups displaying total recoverable space.
- Auto-selection feature with strict safety rules: **at least one original copy per group is always protected and cannot be deleted**.

### 7. 🔧 Windows Native Utilities
- Quick shortcuts to official built-in Windows diagnostic tools:
  - Task Manager (`taskmgr`)
  - Storage Sense Settings (`ms-settings:storagesense`)
  - System Information (`msinfo32`)
  - Drive Optimization & Defragmentation (`dfrgui`)
  - Disk Cleanup (`cleanmgr`)
  - Device Manager (`devmgmt.msc`)
  - Resource Monitor (`resmon`)
  - Control Panel (`control`)

### 8. 🌐 Full Bilingual Support (Arabic & English)
- **Arabic (Default)**: Full Right-to-Left (RTL) layout with tailored typography.
- **English**: Full Left-to-Right (LTR) layout.
- Dynamic runtime language switching from Settings without requiring application restart.

---

## 🔒 Safety & Privacy Principles

- **Standard User Privileges**: Does not require Administrator elevation for routine operations.
- **Zero Telemetry**: No network requests, analytics, tracking, or transmission of file contents.
- **Recycle Bin Integration**: Default file removals move to the Windows Recycle Bin rather than performing permanent unrecoverable deletion.
- **No Registry or System Tampering**: Does not modify Windows services, registry keys, or security settings.

---

## 🛠️ Technology Stack

- **Language**: Python 3.11+
- **GUI Framework**: PySide6 (Qt 6.12)
- **System Telemetry**: psutil
- **File Recycling**: send2trash
- **Testing**: pytest
- **Packaging**: PyInstaller

---

## 🚀 Quick Start

### Prerequisites
Make sure Python 3.11 or newer is installed on your Windows machine:
```bash
python --version
```

### Installation
1. Clone or extract the repository:
   ```bash
   git clone https://github.com/your-username/kimo-pc-manager.git
   cd "kimo-pc-manager"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```
   Or double-click `run.bat`.

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```bash
pytest -v
```

---

## 📦 Building the Windows Executable (.exe)

To build a standalone executable:
```bash
build.bat
```
Or run PyInstaller directly:
```bash
pyinstaller --noconfirm --onedir --windowed --name "KimoPCManager" --icon "assets/icon.ico" --add-data "locales;locales" --add-data "assets;assets" main.py
```
The compiled distribution will be available in:
```
dist/KimoPCManager/KimoPCManager.exe
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
