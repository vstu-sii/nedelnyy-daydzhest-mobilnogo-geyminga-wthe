@echo off
setlocal

if not exist .deploy-state (
    echo ERROR: File .deploy-state not found.
    exit /b 1
)

set /p PREVIOUS_TAG=<.deploy-state

if "%PREVIOUS_TAG%"=="" (
    echo ERROR: Previous version is empty.
    exit /b 1
)

echo Rolling back Production to %PREVIOUS_TAG%...

set IMAGE_TAG=%PREVIOUS_TAG%

docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml pull
if errorlevel 1 exit /b 1

docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml up -d
if errorlevel 1 exit /b 1

echo Production rollback completed.