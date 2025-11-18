#!/bin/bash

# ADMS Server Stop Script
# This script stops the running ADMS server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/adms.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "ADMS server is not running (no PID file found)"
    exit 0
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "ADMS server is not running (stale PID file)"
    rm -f "$PID_FILE"
    exit 0
fi

# Stop the process
echo "Stopping ADMS server (PID: $PID)..."
kill "$PID"

# Wait for process to stop (max 10 seconds)
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "ADMS server stopped successfully"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Process did not stop gracefully, forcing shutdown..."
    kill -9 "$PID"
    sleep 1
fi

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "ADMS server stopped (forced)"
    rm -f "$PID_FILE"
    exit 0
else
    echo "Failed to stop ADMS server"
    exit 1
fi
