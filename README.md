# ZKTeco ADMS Server

A fully functional Automatic Data Master Server for ZKTeco biometric devices.

## Features

- Receives connections from ZKTeco biometric devices (e.g., uFace800 Plus)
- Manages device commands through a web-based interface
- Stores attendance logs from connected devices
- Provides real-time device status monitoring

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

### Method 1: Using the batch file (Windows)
Double-click on `run.bat` or run from command prompt:
```
run.bat
```

### Method 2: Manual start
```
python start_server.py
```

### Method 3: Direct start
```
python main.py
```

## Accessing the Dashboard

Once the server is running, access the web interface at:
http://192.168.1.10:8000

## Supported Device Endpoints

The server listens for ZKTeco device requests on the following endpoints:

- `/iclock/cdata` - Receive device data and attendance logs
- `/iclock/getrequest` - Provide pending commands to devices
- `/iclock/devicecmd` - Receive command responses from devices
- `/iclock/fdata` - Receive fingerprint data

## API Endpoints

### Device Management
- `GET /api/devices` - List all registered devices
- `POST /api/devices/{sn}/command` - Queue a command for a device

### Data Retrieval
- `GET /api/attendance` - Get attendance logs
- `GET /api/commands` - Get command history

## Device Commands

The following commands can be sent to devices:

- `DATA UPDATE` - Sync time
- `RESTART` - Restart device
- `LOCK` - Lock device
- `UNLOCK` - Unlock device
- `LOGDATA` - Retrieve attendance logs
- `POWEROFF` - Shutdown device

## Database Structure

The application uses SQLite for data storage with the following tables:

1. `devices` - Registered device information
2. `device_commands` - Queued and executed commands
3. `attendance_logs` - Collected attendance records

## Troubleshooting

If you encounter issues:

1. Ensure port 8000 is not blocked by firewall
2. Verify the device is configured with the correct server IP (192.168.1.10)
3. Check that all dependencies are installed correctly
4. Review the console logs for error messages

## License

This project is open source and available under the MIT License.