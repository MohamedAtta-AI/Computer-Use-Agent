#!/bin/bash

# Computer Use Agent Backend Startup Script

echo "🚀 Starting Computer Use Agent Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing"
    echo "   Required: ANTHROPIC_API_KEY, SECRET_KEY"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if database is running (if using Docker)
if command -v docker &> /dev/null; then
    echo "🐳 Checking if PostgreSQL is running..."
    if ! docker ps | grep -q postgres; then
        echo "📊 Starting PostgreSQL with Docker..."
        docker run -d \
            --name postgres \
            -e POSTGRES_DB=computer_use_agent \
            -e POSTGRES_USER=user \
            -e POSTGRES_PASSWORD=password \
            -p 5432:5432 \
            postgres:15
        
        echo "⏳ Waiting for PostgreSQL to be ready..."
        sleep 10
    fi
fi

# Create uploads directory
mkdir -p uploads

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start the server
echo "🌐 Starting FastAPI server..."
echo "   API will be available at: http://localhost:8000"
echo "   Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 