#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "Error: Neither 'docker-compose' nor 'docker compose' was found in PATH." >&2
    exit 1
fi

TTY_FLAG=""
if [ ! -t 0 ]; then
    TTY_FLAG="-T"
fi

if $COMPOSE_CMD ps --services --filter "status=running" 2>/dev/null | grep -qx "flask"; then
    echo "Running migrate_project_surveys.py inside running 'flask' container..."
    $COMPOSE_CMD exec $TTY_FLAG flask python migrate_project_surveys.py "$@"
else
    echo "'flask' container is not running. Running migrate_project_surveys.py via temporary container..."
    $COMPOSE_CMD run --rm $TTY_FLAG flask python migrate_project_surveys.py "$@"
fi

if [ -t 0 ]; then
    read -p "Press Enter to continue..."
fi
