#!/bin/bash

# Noxxy Quick Start Script
echo "🚀 Starting Noxxy Note-Taking Application..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please configure it with your MongoDB URI."
    echo ""
fi

# Check if MongoDB is running
echo "🔍 Checking MongoDB connection..."
if ! nc -z localhost 27017 2>/dev/null; then
    echo "⚠️  MongoDB doesn't seem to be running on localhost:27017"
    echo ""
    echo "Start MongoDB with one of these commands:"
    echo "  • brew services start mongodb-community"
    echo "  • docker run -d -p 27017:27017 --name mongodb mongo:latest"
    echo ""
    read -p "Press Enter when MongoDB is running, or Ctrl+C to exit..."
fi

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "📦 Installing dependencies..."
    if command -v uv &> /dev/null; then
        uv sync
    else
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
    fi
fi

echo ""
echo "✅ Starting Flask application..."
echo "🌐 API will be available at: http://localhost:5001"
echo ""
echo "📖 API Endpoints:"
echo "   • Notes:   http://localhost:5001/notes"
echo "   • Bin:     http://localhost:5001/bin"
echo "   • Folders: http://localhost:5001/folders"
echo ""
echo "🧪 Test the API by running: uv run python test_api.py"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
uv run python run.py

