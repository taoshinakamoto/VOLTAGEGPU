@echo off
REM VoltageGPU API Quick Start Script for Windows

echo 🚀 VoltageGPU API Setup
echo ========================

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your configuration before running the API
    echo    Especially set your BACKEND_API_KEY and SECRET_KEY
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo 🔧 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Run the application
echo 🚀 Starting VoltageGPU API...
echo 📍 API will be available at: http://localhost:8000
echo 📚 Documentation available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run with development settings
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
