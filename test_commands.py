import requests
import json

# Test different command formats
device_sn = "JYM6244400083"
base_url = "http://localhost:8000/api/devices"

# Different command formats to test
commands_to_test = [
    "SYNCTIME",           # Simple command
    "DATA QUERY ATTLOG",  # Complex command
    "REBOOT",             # Power command
    "LOCK",               # Device control command
]

print("Testing different command formats:")
for i, command in enumerate(commands_to_test):
    print(f"\n{i+1}. Testing command: {command}")
    
    # Queue the command
    url = f"{base_url}/{device_sn}/command"
    data = {"command": command}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"   Command queued successfully. ID: {result['id']}, Status: {result['status']}")
        else:
            print(f"   Failed to queue command. Status code: {response.status_code}")
    except Exception as e:
        print(f"   Error queuing command: {e}")

print("\nCommands have been queued. Please monitor the device and server logs to see which commands execute successfully.")
