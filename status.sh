#!/bin/bash

# ADMS Server Status Script
# This script checks the status of the ADMS server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/adms.pid"
LOG_FILE="$SCRIPT_DIR/adms.log"

echo "=== ADMS Server Status ==="

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Status: NOT RUNNING (no PID file)"
    exit 1
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Status: RUNNING"
    echo "PID: $PID"
    
    # Show process details
    ps -p "$PID" -o pid,ppid,cmd,%cpu,%mem,etime
    
    # Show last few log lines
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "=== Last 10 log lines ==="
        tail -n 10 "$LOG_FILE"
    fi
    
    exit 0
else
    echo "Status: NOT RUNNING (stale PID file)"
    echo "Stale PID: $PID"
    exit 1
fi
