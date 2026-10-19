@echo off
title Kimo PC Manager
echo ========================================================
echo               Starting Kimo PC Manager
echo ========================================================
echo.

if exist "dist\KimoPCManager-Verified\KimoPCManager\KimoPCManager.exe" (
    start "" "dist\KimoPCManager-Verified\KimoPCManager\KimoPCManager.exe"
    exit /b 0
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in PATH and compiled EXE is not built yet.
    echo Please run build.bat or install Python.
    pause
    exit /b 1
)

python main.py
