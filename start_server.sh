#!/bin/bash

# Production Mistral API Server Startup Script

set -e  # Exit on error

echo "🚀 Starting Mistral Production API Server..."

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $(pwd)"

# Check if virtual environment exists
# if [ ! -d "venv" ]; then
#     echo "📦 Creating virtual environment..."
#     python3 -m venv venv
# fi

# Activate virtual environment
# echo "🔧 Activating virtual environment..."
# source venv/bin/activate

# Install requirements
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export HOST="0.0.0.0"
export PORT="8000"
export WORKERS="1"
export RELOAD="false"
export MODEL_PATH="/teamspace/studios/this_studio/Mentay-Complete-Model-v1/checkpoints/checkpoint_000100/consolidated"
export MAX_TOKENS="4096"
export TEMPERATURE="0.7"
export TOP_P="1.0"
export API_KEYS="token-abc123"
export CORS_ORIGINS="*"
export RATE_LIMIT_PER_MINUTE="60"
export ENABLE_METRICS="true"
export LOG_LEVEL="INFO"
export MAX_CONCURRENT_REQUESTS="100"
export REQUEST_TIMEOUT="300"

# Start the server
echo "🌐 Starting server on ${HOST}:${PORT}..."
echo "📊 Access the API at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
