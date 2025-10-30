import requests
import time
import json

# Configuration
device_sn = "JYM6244400083"
base_url = "http://localhost:8000/api/devices"
monitor_interval = 3  # seconds between checks

def get_device_commands():
    """Get all commands for the device"""
    try:
        response = requests.get(f"{base_url}/{device_sn}/commands")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching commands: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching commands: {e}")
        return []

def get_device_status():
    """Get device status"""
    try:
        response = requests.get(f"{base_url}")
        if response.status_code == 200:
            devices = response.json()
            for device in devices:
                if device['serial_number'] == device_sn:
                    return device
        return None
    except Exception as e:
        print(f"Error fetching device status: {e}")
        return None

def monitor_commands():
    """Monitor command execution in real-time"""
    print("🔍 Real-time Command Execution Monitor")
    print("=" * 60)
    print("Monitoring device:", device_sn)
    print("Press Ctrl+C to stop monitoring")
    print("=" * 60)
    
    last_commands = {}
    
    try:
        while True:
            # Get device status
            device = get_device_status()
            if device:
                print(f"\n📱 Device Status: {device['status']} (Last seen: {device['last_seen']})")
            
            # Get commands
            commands = get_device_commands()
            
            # Check for new or updated commands
            for command in commands:
                cmd_id = command['id']
                status = command['status']
                
                # If this is a new command or status has changed
                if cmd_id not in last_commands or last_commands[cmd_id] != status:
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] 📋 Command #{cmd_id}: {command['command']} -> {status.upper()}")
                    
                    # If command just completed or failed, show details
                    if status in ['completed', 'failed'] and (cmd_id not in last_commands or last_commands[cmd_id] != status):
                        if command['response']:
                            print(f"           Response: {command['response']}")
                        if command['executed_at']:
                            print(f"           Executed: {command['executed_at']}")
                
                last_commands[cmd_id] = status
            
            time.sleep(monitor_interval)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error during monitoring: {e}")

if __name__ == "__main__":
    monitor_commands()