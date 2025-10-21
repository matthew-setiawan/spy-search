#!/bin/sh

# Production run script for Render deployment
# This script is optimized for Render's environment

# Set default port if not provided
if [ -z "$PORT" ]; then
    export PORT=8000
fi

# Set default host
if [ -z "$HOST" ]; then
    export HOST=0.0.0.0
fi

# Set API base URL for frontend
if [ -z "$VITE_API_BASE_URL" ]; then
    export VITE_API_BASE_URL="https://spy-search.onrender.com"
fi

# Check if virtual environment exists and activate it
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    . .venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "Failed to activate virtual environment"
        exit 1
    fi
else
    echo "Virtual environment not found. Please run the setup script first."
    exit 1
fi

# Check if uvicorn is installed
if ! command -v uvicorn >/dev/null 2>&1; then
    echo "uvicorn not found, installing..."
    uv pip install uvicorn
    if [ $? -ne 0 ]; then
        echo "Failed to install uvicorn"
        exit 1
    fi
fi

# Build frontend with correct API URL
echo "Building frontend with API URL: $VITE_API_BASE_URL"
cd frontend
npm run build
cd ..

# Start backend only (Render handles frontend separately if needed)
echo "Starting FastAPI backend on $HOST:$PORT..."
uvicorn main:app --host $HOST --port $PORT --workers 1

# Note: For production, you might want to use gunicorn instead:
# gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind $HOST:$PORT