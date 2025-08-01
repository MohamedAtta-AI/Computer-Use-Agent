@echo off
REM Production Deployment Script for Computer Use Agent Backend (Windows)

echo 🚀 Starting production deployment...

REM Check if .env.prod exists
if not exist .env.prod (
    echo ❌ Error: .env.prod file not found!
    echo Please copy env.prod.example to .env.prod and configure it.
    pause
    exit /b 1
)

echo ✅ Environment variables loaded

REM Create necessary directories
if not exist uploads mkdir uploads
if not exist ssl mkdir ssl

REM Build and start production services
echo 🐳 Building and starting production services...
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

REM Wait for services to be healthy
echo ⏳ Waiting for services to be healthy...
timeout /t 30 /nobreak >nul

REM Check service health
echo 🔍 Checking service health...
docker-compose -f docker-compose.prod.yml ps

REM Run database migrations
echo 🗄️ Running database migrations...
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

REM Test the API
echo 🧪 Testing API health...
timeout /t 10 /nobreak >nul
curl -f http://localhost/health
if errorlevel 1 (
    echo ❌ API health check failed
    docker-compose -f docker-compose.prod.yml logs backend
    pause
    exit /b 1
)

echo ✅ Production deployment completed successfully!
echo 🌐 API is available at: http://localhost
echo 📚 API documentation at: http://localhost/docs
echo 🔍 Health check at: http://localhost/health

REM Show running services
echo 📊 Running services:
docker-compose -f docker-compose.prod.yml ps

pause 