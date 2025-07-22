#!/bin/bash
# Railway startup script to handle python command not found

echo "🚂 Railway Startup Script"
echo "=========================="

# Check if python command exists
if ! command -v python &> /dev/null; then
    echo "⚠️ 'python' command not found, checking for python3..."
    
    if command -v python3 &> /dev/null; then
        echo "✅ Found python3, creating symlink..."
        # Create symlink for python command
        ln -sf $(which python3) /usr/local/bin/python || echo "Failed to create symlink, continuing with python3"
    else
        echo "❌ No Python installation found!"
        exit 1
    fi
fi

# Verify Python version
echo "🐍 Python version:"
python3 --version || python --version

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements-railway.txt || pip install -r requirements-railway.txt

# Start the trading bot
echo "🚀 Starting Railway Trading Bot Worker..."
python3 run_railway_worker.py
