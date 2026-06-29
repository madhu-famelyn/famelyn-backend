#!/bin/bash
# Famelyn Backend – Start script
cd "$(dirname "$0")"

echo "🚀 Setting up/Starting Famelyn Backend on http://127.0.0.1:8000 ..."
echo "   Swagger docs: http://127.0.0.1:8000/docs"
echo ""

# Check if Python virtual environment exists, if not, create it
if [ ! -d "venv_mac" ]; then
    echo "Creating virtual environment venv_mac..."
    python3 -m venv venv_mac
fi

# Activate the macOS virtual environment and install/update requirements
source venv_mac/bin/activate
echo "Checking/installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start uvicorn with hot-reload
echo "Starting backend..."
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
