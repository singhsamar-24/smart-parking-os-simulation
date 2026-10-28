@echo off
title OS PBL Experimental Benchmark Runner - Group 7
color 0B
echo ======================================================================
echo    SMART PARKING MANAGEMENT SYSTEM - OS PBL EXPERIMENTAL TESTBENCH
echo    Course: CCSE0303A ^| Department of CSE-AI ^| NIET Greater Noida
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
            echo [ERROR] Python 3 is not found in standard paths!
            echo Please ensure Python is installed and try again.
            pause
            exit /b 1
        )
    )
)

echo Running Benchmark Experiments and Generating Data Files...
echo.
%PYTHON_CMD% benchmark_experiments.py
echo.
echo Generating Official PDF Report with Matplotlib Charts...
%PYTHON_CMD% generate_pdf_report.py
echo.
echo ======================================================================
echo Benchmark data files and PDF report successfully generated!
echo  - PDF Report: Smart_Parking_OS_PBL_Experimental_Report.pdf
echo  - Data Folder: data\
echo Press any key to exit...
echo ======================================================================
pause >nul
