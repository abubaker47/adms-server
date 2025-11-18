#!/bin/bash

# ADMS Server Restart Script
# This script restarts the ADMS server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Restarting ADMS server..."

# Stop the server
"$SCRIPT_DIR/stop.sh"

# Wait a moment
sleep 1

# Start the server
"$SCRIPT_DIR/start.sh"
