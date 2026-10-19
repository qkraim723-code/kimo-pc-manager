# Kimo PC Manager

A Windows desktop utility for managing files, understanding disk usage, reviewing temporary files, and monitoring system activity from one bilingual interface.

[English](README.md) | [العربية](README_AR.md)

## What it does

- **File Manager:** browse drives and folders; create, rename, copy, and move items; send deletions to the Windows Recycle Bin.
- **Storage Analysis:** scan a selected drive or folder and list the largest folders and files.
- **Safe Cleanup:** review supported temporary-file categories and their sizes before choosing whether to remove them.
- **Duplicate Finder:** find matching files using size checks and SHA-256; keep one copy in each group protected.
- **Performance Monitor:** view CPU, memory, disk activity, and running processes. Ending a process can cause unsaved work in that program to be lost.
- **Windows Tools:** open selected utilities included with Windows.
- **Support settings:** copy the displayed support details, open the Telegram group, and control the optional startup advertisement.

## Languages

The interface is available in **English and Arabic**. English is selected by default; Arabic uses a right-to-left layout. Change the language in Settings.

## Download the app

Open the repository's **Releases** page and download the latest Windows x64 package when a release is published. Extract the complete package and run `KimoPCManager.exe`; this is an *onedir* package, so do not move the executable out of its accompanying files. Windows may ask for administrator approval when launching the packaged app.

If there is no release yet, build the package from source using the steps below.

## Run from source

Requirements: Windows 10 or 11 (64-bit) and Python 3.11 or newer.

```powershell
git clone https://github.com/<owner>/<repository>.git
cd <repository>
python -m pip install -r requirements.txt
python main.py
```

Replace `<owner>` and `<repository>` with the GitHub account and repository name. You can also run `run.bat` from the project folder.

## Build a Windows package

From the project folder, run:

```powershell
build.bat
```

The build uses PyInstaller and creates the app at `dist/KimoPCManager-Verified/KimoPCManager/KimoPCManager.exe`. Keep the full `KimoPCManager` folder together when sharing the app. The build also creates a shortcut in the project folder and on the Windows Desktop.

## Run checks

```powershell
python -m pytest -q
```

## Privacy and safety

- The app does not include analytics or usage telemetry.
- File cleanup and deletion actions are shown in the app before they are applied; ordinary file deletion uses the Windows Recycle Bin where supported.
- The optional startup advertisement is enabled by default. When enabled, the app opens its configured advertisement link in the default web browser at startup. Turn it off in **Settings → Support & Ads**. The browser then connects to that external website under its own privacy policy.
- The packaged Windows executable requests administrator approval through Windows. Running `python main.py` from source does not automatically elevate the Python process.

## Source code and contributions

The Python source is organized into `core/` (system and file services), `ui/` (the interface), `locales/` (English and Arabic text), and `tests/` (automated checks). Bug reports and focused improvements are welcome through GitHub Issues and Pull Requests.

## License

Released under the [MIT License](LICENSE).
