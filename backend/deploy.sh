#!/bin/bash

# Production Deployment Script for Computer Use Agent Backend

set -e

echo "🚀 Starting production deployment..."

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo "❌ Error: .env.prod file not found!"
    echo "Please copy env.prod.example to .env.prod and configure it."
    exit 1
fi

# Load production environment variables
export $(cat .env.prod | grep -v '^#' | xargs)

# Check required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set in .env.prod"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ Error: SECRET_KEY not set in .env.prod"
    exit 1
fi

echo "✅ Environment variables loaded"

# Create necessary directories
mkdir -p uploads
mkdir -p ssl

# Build and start production services
echo "🐳 Building and starting production services..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
docker-compose -f docker-compose.prod.yml ps

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# Test the API
echo "🧪 Testing API health..."
sleep 10
curl -f http://localhost/health || {
    echo "❌ API health check failed"
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
}

echo "✅ Production deployment completed successfully!"
echo "🌐 API is available at: http://localhost"
echo "📚 API documentation at: http://localhost/docs"
echo "🔍 Health check at: http://localhost/health"

# Show running services
echo "📊 Running services:"
docker-compose -f docker-compose.prod.yml ps 