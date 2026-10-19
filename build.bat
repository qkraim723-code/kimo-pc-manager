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

echo Running PyInstaller Build (Standalone One-File Executable)...
pyinstaller --noconfirm --onefile --windowed --name "KimoPCManager" --icon "assets/icon.ico" --add-data "locales;locales" --add-data "assets;assets" main.py

if %errorlevel% equ 0 (
    copy /Y "dist\KimoPCManager.exe" ".\KimoPCManager.exe" >nul
    echo.
    echo ========================================================
    echo  BUILD SUCCESSFUL!
    echo  Standalone EXE ready at:
    echo    1. .\KimoPCManager.exe (Project Root)
    echo    2. .\dist\KimoPCManager.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] Build failed with error code %errorlevel%.
)

pause
