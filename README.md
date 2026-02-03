# ZKTeco ADMS Server

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)

A fully functional Automatic Data Master Server (ADMS) for ZKTeco biometric devices, running on http://SERVER_IP:8080.

## 📑 Table of Contents

- [Overview](#overview)
- [Features](#features-implemented)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [Accessing the Dashboard](#accessing-the-dashboard)
- [Device Configuration](#connecting-devices)
- [API Documentation](#api-endpoints)
- [Database Structure](#database-structure)
- [Technical Implementation](#technical-implementation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project implements a complete ADMS solution for ZKTeco biometric devices with a modern web-based interface for device management and real-time monitoring. The server acts as a central hub for collecting attendance data, managing devices, and sending remote commands to connected ZKTeco biometric terminals.

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

Before you begin, ensure you have the following installed on your system:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package installer) - Usually comes with Python
- **Operating System**: Windows, macOS, or Linux
- **Network access** to communicate with ZKTeco devices
- **Port 8080** available (not used by another application)

## Quick Start

For those who want to get started quickly:

```bash
# 1. Clone the repository
git clone https://github.com/abubaker47/adms-server.git
cd adms-server

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python start_server.py

# 4. Open your browser
# Navigate to http://localhost:8080
```

## Installation

### Step 1: Clone or Download the Repository

```bash
git clone https://github.com/abubaker47/adms-server.git
cd adms-server
```

Or download the ZIP file from GitHub and extract it.

### Step 2: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

**Required packages:**
- `fastapi==0.110.0` - Modern web framework
- `uvicorn==0.27.1` - ASGI server
- `pydantic>=2.10,<3` - Data validation

### Step 3: Verify Installation

Verify that all dependencies are installed correctly:

```bash
python -c "import fastapi, uvicorn, pydantic; print('All dependencies installed successfully!')"
```

## Running the Server

### Option 1: Windows

Double-click `start_adms.bat` or run from command prompt:

```cmd
start_adms.bat
```

This will:
- Automatically install/update required packages
- Start the server on http://0.0.0.0:8080
- Display the server console output

### Option 2: Linux/macOS

Use the provided shell scripts for better control:

```bash
# Start the server (runs in background)
./start.sh

# Check server status
./status.sh

# View server logs
tail -f adms.log

# Restart the server
./restart.sh

# Stop the server
./stop.sh
```

### Option 3: Manual Start (All Platforms)

Start the server directly using Python:

```bash
# Using the wrapper script (recommended)
python start_server.py

# Or directly
python main.py
```

The server will start on `http://0.0.0.0:8080` and will be accessible from any network interface.

## Accessing the Dashboard

Once the server is running, you can access the web interface:

### Local Access
- **URL**: `http://localhost:8080` or `http://127.0.0.1:8080`
- Use this when accessing from the same computer running the server

### Network Access
- **URL**: `http://YOUR_SERVER_IP:8080`
- Replace `YOUR_SERVER_IP` with your actual server IP address (e.g., `http://192.168.1.100:8080`)
- Use this when accessing from other devices on the network

### Dashboard Features

The web interface provides the following capabilities:

1. **Device Management**
   - View all connected devices in real-time
   - See device status (online/offline) with visual indicators
   - View device details (serial number, IP, model, firmware, last activity)
   - Monitor device statistics (total attendance logs, pending commands)

2. **Device Control**
   - **Sync Time**: Synchronize device time with server (Kabul timezone UTC+4:30)
   - **Restart**: Remotely restart the device
   - **Lock/Unlock**: Control device access
   - **Get Logs**: Request attendance data from device
   - **Shutdown**: Power off the device remotely

3. **Data Monitoring**
   - View attendance logs in real-time
   - Track command execution status
   - Filter and search attendance records
   - Export data for reporting

4. **Administrative Actions**
   - Clear queued commands
   - Delete attendance logs
   - Remove devices from the system
   - Refresh data automatically or on-demand

### First Time Access

1. Navigate to `http://localhost:8080` (or use your server's IP)
2. The dashboard will load and show "No devices connected yet" initially
3. Configure your ZKTeco devices to connect to the server (see [Connecting Devices](#connecting-devices))
4. Devices will appear automatically once they make their first connection

## API Endpoints

The server provides both device-facing endpoints (for ZKTeco devices) and management APIs (for web interface and integrations).

### Device Endpoints (ZKTeco Protocol)

These endpoints are used by ZKTeco devices and follow the ADMS protocol:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/iclock/cdata` | GET, POST | Receive attendance logs and device data |
| `/iclock/getrequest` | GET | Provide pending commands to devices |
| `/iclock/devicecmd` | GET, POST | Receive command execution responses |
| `/iclock/fdata` | POST | Receive fingerprint template data |

### Management API Endpoints

#### Device Management

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/devices` | GET | List all registered devices | None |
| `/api/devices/{sn}/info` | GET | Get detailed device information with statistics | `sn` - Device serial number |
| `/api/devices/{sn}/command` | POST | Queue a command for a device | `sn` - Device serial number<br>`command` - Command type (SYNCTIME, RESTART, LOCK, UNLOCK, LOGDATA, POWEROFF, INFO) |
| `/api/devices/{sn}` | DELETE | Remove a device and all related data | `sn` - Device serial number |

#### Data Retrieval

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/attendance` | GET | Get attendance logs | `limit` - Number of records (default: 100) |
| `/api/commands` | GET | Get command history | `device_sn` - Filter by device (optional) |

#### Data Management

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/api/commands/queued` | DELETE | Clear all queued commands | None |
| `/api/attendance` | DELETE | Clear all attendance logs | None |

### API Usage Examples

#### Queue a Command

```bash
curl -X POST "http://localhost:8080/api/devices/ABC123456/command" \
  -H "Content-Type: application/json" \
  -d '{"command": "SYNCTIME"}'
```

#### Get Device List

```bash
curl http://localhost:8080/api/devices
```

#### Get Attendance Logs

```bash
curl "http://localhost:8080/api/attendance?limit=50"
```

#### Get Device Information

```bash
curl http://localhost:8080/api/devices/ABC123456/info
```

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

### Backend Architecture

- **Language**: Python 3.8+
- **Framework**: FastAPI - Modern, fast web framework for building APIs
- **Server**: Uvicorn - Lightning-fast ASGI server
- **Database**: SQLite - Lightweight, serverless database
- **Data Validation**: Pydantic - Data validation using Python type annotations

### Dependencies

```txt
fastapi==0.110.0      # Web framework
uvicorn==0.27.1       # ASGI server
pydantic>=2.10,<3     # Data validation
```

### Frontend

- **Technology Stack**: 
  - HTML5 - Semantic markup
  - TailwindCSS - Utility-first CSS framework
  - Vanilla JavaScript - No heavy frameworks, pure JS for efficiency
  - Font Awesome - Icon library
- **Features**: 
  - Responsive design - Works on desktop, tablet, and mobile
  - Real-time updates - Auto-refresh every 5 seconds
  - Interactive controls - Click-based device management
  - Modern UI - Clean, professional interface

### Architecture Highlights

1. **Auto-Migration System**
   - Database schema automatically updates on server start
   - Adds unique constraints and indexes as needed
   - Handles data migration safely

2. **Command Queue Pattern**
   - Commands stored in database before sending
   - Status tracking: Queued → Sent → Completed/Failed
   - Automatic retry and error handling

3. **Real-Time Device Registration**
   - Zero-configuration device setup
   - Automatic extraction of device information
   - IP and metadata tracking

4. **Timezone Handling**
   - Configured for Kabul timezone (UTC+4:30)
   - Accurate time synchronization with devices
   - Easy to modify for other timezones

## Testing Results

All core functionalities have been successfully tested and validated:

- ✅ **Device auto-registration** - Devices register automatically on first connection
- ✅ **Attendance data parsing and storage** - All attendance records properly captured
- ✅ **Command queuing and execution** - Commands successfully queued and sent
- ✅ **Command response handling** - Device responses properly processed
- ✅ **Web dashboard functionality** - All UI features working correctly
- ✅ **API endpoints** - All REST APIs tested and functional
- ✅ **Database migration** - Schema updates work seamlessly
- ✅ **Duplicate prevention** - Unique constraints prevent duplicate records
- ✅ **Time synchronization** - Timezone handling works correctly

## Connecting Devices

To connect your ZKTeco biometric devices to the ADMS server:

### Device Configuration Steps

1. **Access Device Settings**
   - Navigate to device's communication or network settings menu
   - Look for "Server" or "ADMS" configuration section

2. **Configure Server Connection**
   - **Server IP Address**: Enter your server's IP address (e.g., `192.168.1.100`)
   - **Port**: Set to `8080`
   - **Protocol**: Enable ADMS or HTTP protocol
   - **Upload Mode**: Select "Real-time" or "Auto" for immediate data sync

3. **Save and Test**
   - Save the configuration
   - The device will automatically attempt to connect
   - Check the dashboard to see if the device appears

### Automatic Device Registration

- Devices are **automatically registered** when they first connect
- No manual registration is required
- The server captures device information automatically:
  - Serial number
  - IP address
  - Model (if provided)
  - Firmware version (if provided)

### Verification

After configuration, verify the connection:

1. Check the web dashboard at `http://YOUR_SERVER_IP:8080`
2. The device should appear in the devices list
3. Status should show as "Online" (green indicator)
4. Last activity time should be recent

### Network Requirements

- Ensure both the server and devices are on the same network or can reach each other
- Port 8080 must be open on the server's firewall
- No NAT/routing issues between devices and server

## Future Enhancements

1. **Authentication**: Add user authentication for the web interface
2. **WebSocket Support**: Implement real-time updates using WebSockets
3. **Device Groups**: Add support for organizing devices into groups
4. **Reporting**: Add attendance reporting and analytics
5. **Backup**: Implement database backup functionality
6. **Logging**: Enhanced logging and monitoring capabilities

## Troubleshooting

### Common Issues and Solutions

#### Server Won't Start

**Problem**: Error when starting the server

**Solutions**:
```bash
# Check if port 8080 is already in use
# Linux/macOS:
lsof -i :8080
# Windows:
netstat -ano | findstr :8080

# If port is in use, either stop the other application or change the port in start_server.py
```

**Problem**: `ModuleNotFoundError` when starting

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify Python version (must be 3.8+)
python --version
```

#### Devices Not Connecting

**Problem**: Devices don't appear in the dashboard

**Solutions**:
1. **Check network connectivity**
   ```bash
   # Ping the server from the device's network
   ping YOUR_SERVER_IP
   ```

2. **Verify firewall settings**
   - Ensure port 8080 is open on the server
   - Check both Windows Firewall and any antivirus software
   - On Linux: `sudo ufw allow 8080/tcp`

3. **Verify device configuration**
   - Server IP must match your actual server IP
   - Port must be set to 8080
   - ADMS protocol must be enabled

4. **Check server logs**
   ```bash
   # Linux/macOS
   tail -f adms.log
   
   # Windows - check console output
   ```

#### Attendance Data Not Appearing

**Problem**: Devices are connected but no attendance logs show up

**Solutions**:
1. **Trigger data sync manually**
   - Use "Get Logs" button in the dashboard for the specific device
   - Or send command via API: `POST /api/devices/{sn}/command` with `{"command": "LOGDATA"}`

2. **Check device settings**
   - Ensure upload mode is set to "Real-time" or "Auto"
   - Verify device has attendance data to upload

3. **Check database**
   ```bash
   # Connect to database to verify data
   sqlite3 adms.db "SELECT COUNT(*) FROM attendance_logs;"
   ```

#### Time Sync Issues

**Problem**: Device time is not syncing correctly

**Solutions**:
1. **Verify timezone configuration**
   - Server is configured for Kabul timezone (UTC+4:30)
   - If you need a different timezone, modify the `get_kabul_time()` function in `main.py`

2. **Send manual time sync**
   - Use "Sync Time" button in the dashboard
   - Device will sync to server's current time

#### Commands Not Executing

**Problem**: Commands remain in "Queued" status

**Solutions**:
1. **Check device online status**
   - Device must be online to receive commands
   - Verify "Last Activity" time is recent

2. **Wait for device polling**
   - Devices poll the server periodically (usually every 30-60 seconds)
   - Commands will be sent on next poll

3. **Clear stuck commands**
   - Use "Clear Queued Commands" in the dashboard
   - Or via API: `DELETE /api/commands/queued`

#### Database Issues

**Problem**: Database errors or corruption

**Solutions**:
```bash
# Backup existing database
cp adms.db adms.db.backup

# Check database integrity
sqlite3 adms.db "PRAGMA integrity_check;"

# If corrupted, restore from backup or delete and restart (data will be lost)
rm adms.db
# Restart server - it will create a new database
```

#### Permission Issues

**Problem**: Permission denied errors

**Solutions**:
```bash
# Linux/macOS - make scripts executable
chmod +x *.sh

# Ensure write permissions for database
chmod 644 adms.db
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs** - Most errors are logged with detailed information
2. **Review server console output** - Errors appear in real-time
3. **Verify all prerequisites** - Python version, dependencies, network access
4. **Check device compatibility** - Ensure device supports ADMS protocol
5. **Open an issue** - Report bugs or request features on GitHub

### Debug Mode

To enable verbose logging for troubleshooting:

Edit `main.py` and change the logging level:
```python
logging.basicConfig(level=logging.DEBUG)  # Change from INFO to DEBUG
```

## Contributing

Contributions are welcome! Here's how you can help improve the ZKTeco ADMS Server:

### Reporting Issues

If you find a bug or have a feature request:

1. **Check existing issues** - Make sure it hasn't been reported already
2. **Create a new issue** on GitHub with:
   - Clear description of the problem or feature
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or error messages

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/adms-server.git
   cd adms-server
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style and conventions
   - Add comments for complex logic
   - Test your changes thoroughly
   - Update documentation if needed

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues (#issue_number)
   - Explain the benefit and impact of your changes

### Development Guidelines

- **Code Style**: Follow PEP 8 for Python code
- **Testing**: Test all changes manually and ensure no regressions
- **Documentation**: Update README.md and code comments as needed
- **Compatibility**: Ensure changes work on Python 3.8+
- **Dependencies**: Minimize new dependencies; justify if needed

### Areas for Contribution

- Bug fixes and performance improvements
- New features (see [Future Enhancements](#future-enhancements))
- Documentation improvements
- Test coverage
- Internationalization (i18n)
- UI/UX enhancements

## Future Enhancements

Planned improvements for future releases:

### Authentication & Authorization
- User login system for web interface
- Role-based access control (admin, viewer, operator)
- API token authentication for integrations
- Session management and security

### Real-Time Features
- WebSocket support for live dashboard updates
- Push notifications for critical events
- Real-time attendance monitoring
- Live command execution feedback

### Advanced Device Management
- Device grouping and organization
- Bulk operations (command multiple devices simultaneously)
- Device templates and configuration profiles
- Device health monitoring and alerts

### Reporting & Analytics
- Attendance reports (daily, weekly, monthly, custom)
- Export to CSV, Excel, PDF formats
- Graphs and charts for attendance patterns
- Device usage statistics and analytics
- Shift management and overtime tracking

### Data Management
- Automatic database backup and restore
- Data retention policies and archiving
- Database cleanup and optimization tools
- Import/export data functionality

### Enhanced Logging & Monitoring
- Structured logging (JSON format)
- Log rotation and archival
- Integration with external log management systems
- Comprehensive audit trail for all operations
- Performance monitoring and metrics

### Additional Features
- Email notifications for events and alerts
- SMS integration for critical notifications
- Multi-timezone support for global deployments
- Custom command creation and scripting
- Firmware update management
- Multi-language support (i18n)
- Dark mode for web interface
- Mobile app companion (future consideration)

## License

This project is open source and available under the **MIT License**.

You are free to use, modify, and distribute this software for personal or commercial purposes.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- UI powered by [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS framework
- Icons from [Font Awesome](https://fontawesome.com/) - Popular icon library

## Support

For questions, issues, or feature requests:
- **GitHub Issues**: [Create an issue](https://github.com/abubaker47/adms-server/issues)
- **Documentation**: This README and inline code comments
- **Community**: Share your experience and help others

## Conclusion

The **ZKTeco ADMS Server** is a complete, production-ready solution for managing ZKTeco biometric devices. It provides all the core functionality needed to:

- ✅ Register and manage devices automatically
- ✅ Collect and store attendance data reliably
- ✅ Send remote commands to devices
- ✅ Monitor device status in real-time
- ✅ Access data through a modern web interface
- ✅ Integrate with other systems via REST API

Whether you're managing a single device or an entire network of biometric terminals, this server provides the tools you need for effective attendance management.

**Get started today** and simplify your biometric device management!