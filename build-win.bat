@echo off
setlocal

rem ============================================================
rem  Build script - package Piggy Meadow for Windows
rem  Output: dist\PiggyMeadow.exe (standalone, no Python required)
rem  Usage:   build-win.bat  (run in cmd / PowerShell)
rem ============================================================

rem Change to script directory
cd /d "%~dp0"

rem ---- 1. Create virtual environment if missing ----
if not exist venv (
    echo [1/3] Creating virtual environment venv ...
    rem Prefer Python 3.12: pygame / PyInstaller have no wheels for 3.13+/3.14 yet
    set "PYTHON_EXE=python"
    py -3.12 -c "import sys" >nul 2>&1 && set "PYTHON_EXE=py -3.12"
    %PYTHON_EXE% -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv. Make sure Python 3.12 is installed and in PATH.
        pause
        exit /b 1
    )
)

rem ---- 2. Install dependencies ----
echo [2/3] Installing dependencies ^(pygame / Pillow / PyInstaller^) ...
venv\Scripts\python.exe -m pip install --quiet pygame Pillow pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

rem ---- 3. Build with PyInstaller ----
echo [3/3] Building with PyInstaller ...
venv\Scripts\pyinstaller.exe --onefile --windowed ^
    --icon=processed\icon.ico ^
    --name PiggyMeadow ^
    --add-data "processed;processed" ^
    main.py
if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

rem ---- Cleanup intermediate files ----
if exist build rmdir /s /q build
if exist PiggyMeadow.spec del /q PiggyMeadow.spec

echo.
echo Build complete: %cd%\dist\PiggyMeadow.exe
dir dist\PiggyMeadow.exe

pause
endlocal
