#!/bin/bash
# Quick Test Script for Command Execution Fix

echo "============================================================"
echo "ADMS Command Execution - Quick Test"
echo "============================================================"
echo ""

# Check if server is running
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo "✅ Server is running"
else
    echo "❌ Server is NOT running"
    echo ""
    echo "To start the server:"
    echo "  cd /root/aogc"
    echo "  python3 start_server.py"
    echo ""
    exit 1
fi

echo ""
echo "Testing API endpoints..."
echo ""

# Test devices endpoint
echo "1. Checking devices..."
DEVICES=$(curl -s http://localhost:8080/api/devices)
DEVICE_COUNT=$(echo "$DEVICES" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo "   Devices registered: $DEVICE_COUNT"

if [ "$DEVICE_COUNT" -eq "0" ]; then
    echo "   ⚠️  No devices registered yet"
    echo "   Devices will appear when they connect to the server"
else
    echo "   ✅ Devices found"
    # Get first device SN
    DEVICE_SN=$(echo "$DEVICES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['serial_number'] if data else '')" 2>/dev/null)
    echo "   First device: $DEVICE_SN"
fi

echo ""
echo "2. Checking commands..."
COMMANDS=$(curl -s http://localhost:8080/api/commands)
COMMAND_COUNT=$(echo "$COMMANDS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo "   Total commands: $COMMAND_COUNT"

if [ "$COMMAND_COUNT" -gt "0" ]; then
    echo ""
    echo "Recent command statuses:"
    echo "$COMMANDS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for cmd in data[:5]:
        print(f\"   - ID {cmd['id']}: {cmd['command']} → {cmd['status']}\")
except:
    pass
" 2>/dev/null
fi

echo ""
echo "============================================================"
echo "Test New Command"
echo "============================================================"
echo ""

if [ -n "$DEVICE_SN" ]; then
    echo "Testing command on device: $DEVICE_SN"
    echo ""
    echo "Sending SYNCTIME command..."
    
    RESULT=$(curl -s -X POST http://localhost:8080/api/devices/$DEVICE_SN/command \
        -H "Content-Type: application/json" \
        -d '{"command":"SYNCTIME"}')
    
    if echo "$RESULT" | grep -q "id"; then
        CMD_ID=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
        echo "✅ Command queued successfully!"
        echo "   Command ID: $CMD_ID"
        echo ""
        echo "Expected flow:"
        echo "  1. Device polls server (within 30-60 seconds)"
        echo "  2. Device receives: C:$CMD_ID:SYNCTIME"
        echo "  3. Device executes command"
        echo "  4. Device acknowledges: /iclock/devicecmd?SN=$DEVICE_SN&ID=$CMD_ID&Response=OK"
        echo "  5. Command status updates to 'completed'"
        echo ""
        echo "Check command status:"
        echo "  curl http://localhost:8080/api/commands | grep -A 2 '\"id\": $CMD_ID'"
        echo ""
        echo "Watch server logs:"
        echo "  tail -f /tmp/adms_server.log  # (if logging to file)"
        echo "  or check the terminal where start_server.py is running"
    else
        echo "❌ Failed to queue command"
        echo "   Response: $RESULT"
    fi
else
    echo "⚠️  No device available for testing"
    echo ""
    echo "To test with a real device:"
    echo "  1. Configure device to point to this server"
    echo "  2. Set server IP in device settings"
    echo "  3. Wait for device to connect"
    echo "  4. Device will appear in dashboard"
    echo "  5. Run this script again"
fi

echo ""
echo "============================================================"
echo "Manual Testing Steps"
echo "============================================================"
echo ""
echo "1. Open dashboard:"
echo "   http://localhost:8080"
echo ""
echo "2. Verify device appears in 'Devices' tab"
echo ""
echo "3. Click 'Command' button on device"
echo ""
echo "4. Select a command (e.g., 'Sync Time')"
echo ""
echo "5. Switch to 'Commands' tab"
echo ""
echo "6. Watch status change:"
echo "   queued → sent → completed"
echo ""
echo "7. Check 'Response' column shows 'OK'"
echo ""
echo "============================================================"
echo "Troubleshooting"
echo "============================================================"
echo ""
echo "If command stays in 'sent' status:"
echo "  • Check device is online (green dot in Devices tab)"
echo "  • Verify device firmware supports ADMS protocol"
echo "  • Check network connectivity"
echo "  • Review server logs for errors"
echo "  • Ensure device polling interval is reasonable (30-60s)"
echo ""
echo "If command fails immediately:"
echo "  • Check command syntax is correct"
echo "  • Verify device supports the command"
echo "  • Check device is not in restricted mode"
echo ""
echo "============================================================"
