import requests
import json

# Send a REBOOT command to the device
url = "http://localhost:8000/api/devices/JYM6244400083/command"
data = {"command": "REBOOT"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")