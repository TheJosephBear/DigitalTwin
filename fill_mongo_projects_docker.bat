@echo off
cd /d "%~dp0"

REM Detect docker compose or docker-compose
docker compose version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "COMPOSE_CMD=docker compose"
) else (
    docker-compose version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "COMPOSE_CMD=docker-compose"
    ) else (
        echo Error: Neither 'docker compose' nor 'docker-compose' was found.
        pause
        exit /b 1
    )
)

echo Checking for running flask container...
%COMPOSE_CMD% ps --services --filter "status=running" 2>nul | findstr /x /c:"flask" >nul
if %ERRORLEVEL% EQU 0 (
    echo Running fill_mongo_projects.py inside running 'flask' container...
    %COMPOSE_CMD% exec flask python fill_mongo_projects.py --owner x %*
) else (
    echo 'flask' container is not running. Running via temporary container...
    %COMPOSE_CMD% run --rm flask python fill_mongo_projects.py --owner x %*
)

pause
