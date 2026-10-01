@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

where docker >nul 2>nul
if %errorlevel% equ 0 (
    docker compose version >nul 2>nul
    if !errorlevel! equ 0 (
        set COMPOSE_CMD=docker compose
    )
)

if not defined COMPOSE_CMD (
    where docker-compose >nul 2>nul
    if !errorlevel! equ 0 (
        set COMPOSE_CMD=docker-compose
    )
)

if not defined COMPOSE_CMD (
    echo Error: Neither 'docker compose' nor 'docker-compose' was found in PATH.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('!COMPOSE_CMD! ps --services --filter "status=running" 2^>nul') do (
    if "%%i"=="flask" set RUNNING=1
)

if defined RUNNING (
    echo Running migrate_project_surveys.py inside running 'flask' container...
    !COMPOSE_CMD! exec flask python migrate_project_surveys.py %*
) else (
    echo 'flask' container is not running. Running migrate_project_surveys.py via temporary container...
    !COMPOSE_CMD! run --rm flask python migrate_project_surveys.py %*
)

pause
