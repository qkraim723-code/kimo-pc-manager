@echo off
title Building Kimo PC Manager EXE
echo ========================================================
echo             Building Kimo PC Manager with PyInstaller
echo ========================================================
echo.

where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller is not installed. Installing dependencies...
    pip install -r requirements.txt
)

echo Generating application icons if not present...
if not exist assets\icon.ico (
    python assets\generate_icon.py
)

echo Running PyInstaller Build...
pyinstaller --noconfirm --onedir --windowed --name "KimoPCManager" --icon "assets/icon.ico" --add-data "locales;locales" --add-data "assets;assets" main.py

if %errorlevel% equ 0 (
    echo.
    echo Creating application shortcuts with custom icon...
    powershell -ExecutionPolicy Bypass -File create_shortcut.ps1 >nul
    echo.
    echo ========================================================
    echo  BUILD SUCCESSFUL!
    echo.
    echo  Application ready to run from:
    echo    1. Shortcut: "Kimo PC Manager.lnk" (in this folder and on Desktop)
    echo    2. Executable: "dist\KimoPCManager\KimoPCManager.exe"
    echo ========================================================
) else (
    echo.
    echo [ERROR] Build failed with error code %errorlevel%.
)

pause
