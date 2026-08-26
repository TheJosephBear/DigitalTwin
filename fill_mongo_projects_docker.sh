#!/bin/bash
set -e

# Navigate to project root directory where docker-compose.yml resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detect docker-compose or docker compose
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

# Check if flask container is already running
if $COMPOSE_CMD ps --services --filter "status=running" 2>/dev/null | grep -qx "flask"; then
    echo "Running fill_mongo_projects.py inside running 'flask' container..."
    $COMPOSE_CMD exec $TTY_FLAG flask python fill_mongo_projects.py --owner x "$@"
else
    echo "'flask' container is not running. Running fill_mongo_projects.py via temporary container..."
    $COMPOSE_CMD run --rm $TTY_FLAG flask python fill_mongo_projects.py --owner x "$@"
fi

if [ -t 0 ]; then
    read -p "Press Enter to continue..."
fi
