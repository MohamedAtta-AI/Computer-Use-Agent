@echo off
REM Computer Use Agent Backend Startup Script for Windows

echo 🚀 Starting Computer Use Agent Backend...

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy env.example .env
    echo ⚠️  Please edit .env file with your configuration before continuing
    echo    Required: ANTHROPIC_API_KEY, SECRET_KEY
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo 🐍 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create uploads directory
if not exist uploads mkdir uploads

REM Run database migrations
echo 🗄️  Running database migrations...
alembic upgrade head

REM Start the server
echo 🌐 Starting FastAPI server...
echo    API will be available at: http://localhost:8000
echo    Documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 