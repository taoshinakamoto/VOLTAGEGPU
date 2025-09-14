#!/bin/bash

# VoltageGPU API Quick Start Script

echo "🚀 VoltageGPU API Setup"
echo "========================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before running the API"
    echo "   Especially set your BACKEND_API_KEY and SECRET_KEY"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the application
echo "🚀 Starting VoltageGPU API..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 Documentation available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with development settings
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
