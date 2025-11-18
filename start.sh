#!/bin/bash

# ADMS Server Start Script
# This script starts the ADMS server as a background process

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/adms.pid"
LOG_FILE="$SCRIPT_DIR/adms.log"

# Check if server is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "ADMS server is already running (PID: $PID)"
        exit 1
    else
        echo "Removing stale PID file"
        rm -f "$PID_FILE"
    fi
fi

# Change to script directory
cd "$SCRIPT_DIR"

# Start the server in background
echo "Starting ADMS server..."
nohup python3 main.py > "$LOG_FILE" 2>&1 &
PID=$!

# Save PID to file
echo $PID > "$PID_FILE"

# Wait a moment to check if it started successfully
sleep 2

if ps -p "$PID" > /dev/null 2>&1; then
    echo "ADMS server started successfully (PID: $PID)"
    echo "Log file: $LOG_FILE"
    echo "To view logs: tail -f $LOG_FILE"
else
    echo "Failed to start ADMS server. Check $LOG_FILE for errors"
    rm -f "$PID_FILE"
    exit 1
fi
