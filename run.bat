@echo off
title Kimo PC Manager
echo ========================================================
echo               Starting Kimo PC Manager
echo ========================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in PATH. Please install Python 3.11 or newer.
    pause
    exit /b 1
)

python main.py

if %errorlevel% neq 0 (
    echo.
    echo Application exited with an error code %errorlevel%.
    pause
)
