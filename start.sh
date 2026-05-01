#!/bin/bash
# EventHorizon SOC - Quick Start Script (Mac/Linux)
# This script sets up and runs the application locally

echo ""
echo "========================================"
echo "  EventHorizon SOC - Local Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11+ from https://www.python.org"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "NOTE: Edit .env and add your GEMINI_API_KEY"
    echo "https://ai.google.dev to get a free API key"
    echo ""
    read -p "Press Enter to continue..."
fi

# Run the application
echo ""
echo "========================================"
echo "  Starting EventHorizon SOC..."
echo "========================================"
echo ""
echo "Dashboard: http://localhost:8000"
echo "Health:    http://localhost:8000/health"
echo "Docs:      http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
