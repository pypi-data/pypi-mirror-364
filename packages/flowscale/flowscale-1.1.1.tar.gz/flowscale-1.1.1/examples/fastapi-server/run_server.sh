#!/bin/bash

# Flowscale FastAPI Server Startup Script

echo "🚀 Starting Flowscale FastAPI Server..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists and has been configured
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API credentials"
    exit 1
fi

if grep -q "your_api_key_here" .env; then
    echo "⚠️  Warning: Please update your .env file with actual API credentials"
    echo "Current .env content:"
    cat .env
    echo ""
    echo "Update FLOWSCALE_API_KEY and FLOWSCALE_API_URL before running the server"
    echo ""
fi

echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation available at:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload