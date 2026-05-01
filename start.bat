@echo off
REM EventHorizon SOC - Quick Start Script (Windows)
REM This script sets up and runs the application locally

echo.
echo ========================================
echo   EventHorizon SOC - Local Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed
echo.

REM Create .env if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo NOTE: Edit .env and add your GEMINI_API_KEY
    echo https://ai.google.dev to get a free API key
    echo.
    pause
)

REM Run the application
echo.
echo ========================================
echo   Starting EventHorizon SOC...
echo ========================================
echo.
echo Dashboard: http://localhost:8000
echo Health:    http://localhost:8000/health
echo Docs:      http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
