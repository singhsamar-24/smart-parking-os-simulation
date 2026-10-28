@echo off
title Smart Parking Management System - OS PBL
color 0A
echo ======================================================================
echo    SMART PARKING MANAGEMENT SYSTEM - OPERATING SYSTEM PBL PROJECT
echo    Course: CCSE0303A ^| Group 7 ^| NIET Greater Noida (CSE-AI)
echo ======================================================================
echo.

set PYTHON_CMD=python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py -3.11 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py -3.11
    ) else (
        py -3 --version >nul 2>&1
        if %errorlevel% equ 0 (
            set PYTHON_CMD=py -3
        ) else if exist "C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\python.exe" (
            set PYTHON_CMD="C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\python.exe"
        ) else if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
            set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        ) else (
            echo [ERROR] Python 3.11 is not found in standard paths!
            echo Please ensure Python is installed and try again.
            pause
            exit /b 1
        )
    )
)

echo Starting Smart Parking OS Server...
%PYTHON_CMD% main.py 8000
pause
