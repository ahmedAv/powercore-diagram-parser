@echo off
echo ======================================
echo Starting FastAPI + Nginx with Docker Compose
echo ======================================

REM Build and run containers in detached mode
docker-compose up -d

echo ======================================
echo Containers are now running.
echo Visit http://localhost:8000/docs
echo ======================================
pause