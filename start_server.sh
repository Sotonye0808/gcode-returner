#!/bin/bash
# Django Development Server Startup Script for Linux/macOS
# This script activates the virtual environment and starts the Django development server

echo "Starting GCode Returner API..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating virtual environment..."
    python3 -m venv venv
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your configuration before running again."
    exit 1
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create media and logs directories
mkdir -p media logs

# Start development server
echo
echo "Starting Django development server..."
echo "API will be available at: http://localhost:8000/api/"
echo "Health check: http://localhost:8000/api/health/"
echo
python manage.py runserver
