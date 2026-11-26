@echo off
chcp 65001 >nul
title Parrot Voice Client — Launcher

cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.10 - 3.12 from https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

if not exist "venv" (
    echo [1/2] Creating isolated environment...
    python -m venv venv
)

echo [2/2] Checking required libraries...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt --quiet

echo Starting Parrot Voice Client in system tray...
start "" pythonw parrot_client.py
exit