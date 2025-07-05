@echo off
REM Django Development Server Startup Script for Windows
REM This script activates the virtual environment and starts the Django development server

echo Starting GCode Returner API...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your configuration before running again.
    pause
    exit /b
)

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Create media and logs directories
if not exist "media" mkdir media
if not exist "logs" mkdir logs

REM Start development server
echo.
echo Starting Django development server...
echo API will be available at: http://localhost:8000/api/
echo Health check: http://localhost:8000/api/health/
echo.
python manage.py runserver

pause
