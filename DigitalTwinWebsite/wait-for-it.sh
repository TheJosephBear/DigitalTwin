#!/bin/sh
# wait-for-it.sh

# Usage:
#   wait-for-it.sh host:port [-- command args]
#   wait-for-it.sh mongodb:27017 -- python app.py
#
# The script waits for the host and port to become available before executing
# the specified command with arguments.

set -e

# Parse host and port from the first argument
if [ -z "$1" ]; then
  echo "Error: you need to provide a host:port as the first argument"
  exit 1
fi

# Parse the host and port without using arrays (sh-compatible)
host=$(echo "$1" | cut -d ":" -f 1)
port=$(echo "$1" | cut -d ":" -f 2)
shift

# Parse command from the arguments after --
cmd=""
if [ "$1" = "--" ]; then
  shift
  cmd="$@"
fi

# Function to check if a port is open
wait_for() {
  echo "Waiting for $host:$port..."

  start_time=$(date +%s)
  timeout=30

  while ! nc -z "$host" "$port" >/dev/null 2>&1; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))

    if [ $elapsed -gt $timeout ]; then
      echo "Timeout reached after $timeout seconds. $host:$port is still not available."
      echo "Continuing anyway..."
      break
    fi

    echo "Still waiting for $host:$port... ($elapsed seconds elapsed)"
    sleep 1
  done

  if nc -z "$host" "$port" >/dev/null 2>&1; then
    echo "$host:$port is available after $elapsed seconds"
  fi
}

# Wait for the host and port to be available
wait_for

# Execute the given command if provided
if [ -n "$cmd" ]; then
  echo "Executing command: $cmd"
  exec $cmd
fi