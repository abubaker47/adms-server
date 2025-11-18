# ZKTeco ADMS Server

A fully functional Automatic Data Master Server (ADMS) for ZKTeco biometric devices, running on http://SERVER_IP:8080.

## Overview

This project implements a complete ADMS solution for ZKTeco biometric devices with a modern web-based interface for device management and real-time monitoring.

## Features Implemented

### 1. Core ADMS Server
- **Framework**: FastAPI-based HTTP server
- **Listening Address**: http://SERVER_IP:8080
- **Auto-registration**: Devices are automatically registered when they first connect
- **Real-time monitoring**: Live device status tracking
- **Timezone Support**: Configured for Kabul timezone (UTC+4:30) for accurate time synchronization
- **Database Migration**: Automatic database schema migration on startup

### 2. Device Management
- **Device Information Storage**:
  - Serial number
  - IP address
  - Model (optional)
  - Firmware version (optional)
  - Last activity time
  - Status (online/offline)

### 3. Web-based Dashboard
- **Technology**: HTML + TailwindCSS + JavaScript
- **Features**:
  - Real-time device list with status indicators
  - Device action buttons (Sync Time, Restart, Lock, Unlock, Get Logs, Shutdown)
  - Command status tracking
  - Attendance log display
  - Responsive design

### 4. Command Queue System
- **Database Storage**: Commands are stored in the `device_commands` table
- **Status Tracking**: Queued → Sent → Completed/Failed
- **Remote Control**: Full device management capabilities

### 5. Attendance Data Handling
- **Real-time Processing**: Processes attendance records as they arrive
- **Comprehensive Storage**: All attendance data with detailed fields
- **Data Integrity**: Proper parsing and validation
- **Duplicate Prevention**: Unique constraint on attendance logs (device_sn, user_id, timestamp)
- **Optimized Queries**: Indexed for faster data retrieval

## Prerequisites

- Python 3.11+
- Windows, macOS, or Linux operating system

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Server

### Windows
Double-click `start_adms.bat` or run from command prompt:
```
start_adms.bat
```

### Linux/macOS
Use the provided shell scripts:
```bash
# Start the server
./start.sh

# Stop the server
./stop.sh

# Restart the server
./restart.sh

# Check server status
./status.sh
```

### Manual Start (All platforms)
```
python start_server.py
```
or
```
python main.py
```

## Accessing the Dashboard

Once the server is running, access the web interface at:
http://SERVER_IP:8080

### Using the Web Interface
1. Navigate to http://SERVER_IP:8080
2. View connected devices in real-time
3. Send commands using device action buttons
4. Monitor attendance logs and command status
5. View detailed device information and statistics
6. Clear queued commands, attendance logs, or remove devices

## Supported Device Endpoints

The server listens for ZKTeco device requests on the following endpoints:

- `/iclock/cdata` - Receive device data and attendance logs
- `/iclock/getrequest` - Provide pending commands to devices
- `/iclock/devicecmd` - Receive command responses from devices
- `/iclock/fdata` - Receive fingerprint data

## API Endpoints

### Device Management
- `GET /api/devices` - List all registered devices
- `GET /api/devices/{sn}/info` - Get detailed device information with statistics
- `POST /api/devices/{sn}/command` - Queue a command for a device
- `DELETE /api/devices/{sn}` - Remove a device and all its related data

### Data Retrieval
- `GET /api/attendance` - Get attendance logs
- `GET /api/commands` - Get command history

### Data Management
- `DELETE /api/commands/queued` - Clear all queued commands
- `DELETE /api/attendance` - Clear all attendance logs

## Device Commands

The following commands can be sent to devices:

- `SYNCTIME` - Sync time with Kabul timezone (UTC+4:30)
- `RESTART` - Restart device
- `LOCK` - Lock device
- `UNLOCK` - Unlock device
- `LOGDATA` - Retrieve attendance logs
- `POWEROFF` - Shutdown device
- `INFO` - Request device information update

## Database Structure

The application uses SQLite for data storage with the following tables:

### Tables:
- **`devices`**: Registered device information
  - Serial number (unique), IP address, model, firmware version
  - Last activity time and status tracking
- **`device_commands`**: Queued and executed commands
  - Command type, status, timestamps
  - Response tracking and error handling
  - Foreign key reference to devices table
- **`attendance_logs`**: Collected attendance records
  - Device serial number, user ID, timestamp
  - Verify mode and status information
  - Unique constraint on (device_sn, user_id, timestamp) to prevent duplicates
  - Indexed for optimized queries by device, user, and timestamp

## Technical Implementation

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: SQLite
- **Dependencies**: 
  - fastapi>=0.100.0
  - uvicorn>=0.38.0
  - pydantic>=2.0.0

### Frontend
- **Technology**: HTML + TailwindCSS + JavaScript
- **Features**: 
  - Responsive design
  - Real-time updates
  - Interactive controls

## Testing Results

All core functionalities have been successfully tested:

1. ✅ Device auto-registration
2. ✅ Attendance data parsing and storage
3. ✅ Command queuing and execution
4. ✅ Command response handling
5. ✅ Web dashboard functionality
6. ✅ API endpoints

## Connecting Devices

1. Configure ZKTeco devices to use server IP: SERVER_IP
2. Set port to: 8080
3. Enable ADMS protocol on the device
4. Devices will auto-register upon first connection

## Future Enhancements

1. **Authentication**: Add user authentication for the web interface
2. **WebSocket Support**: Implement real-time updates using WebSockets
3. **Device Groups**: Add support for organizing devices into groups
4. **Reporting**: Add attendance reporting and analytics
5. **Backup**: Implement database backup functionality
6. **Logging**: Enhanced logging and monitoring capabilities

## Troubleshooting

If you encounter issues:

1. Ensure port 8080 is not blocked by firewall
2. Verify the device is configured with the correct server IP (SERVER_IP)
3. Check that all dependencies are installed correctly
4. Review the console logs for error messages
5. Verify the virtual environment is activated when running the server
6. Check database permissions if encountering data storage issues
7. Verify server timezone is correctly set to Asia/Kabul for time synchronization

## License

This project is open source and available under the MIT License.

## Conclusion

The ZKTeco ADMS Server is a complete, production-ready solution for managing ZKTeco biometric devices. It provides all the core functionality needed to register devices, collect attendance data, and remotely manage devices through a user-friendly web interface.