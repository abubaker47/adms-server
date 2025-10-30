import requests
import json
import time

# Configuration
device_sn = "JYM6244400083"
base_url = "http://localhost:8000/api/devices"
check_interval = 5  # seconds to wait between checks

# Different command formats to test
test_scenarios = [
    {
        "name": "Standard REBOOT",
        "command": "REBOOT",
        "description": "Standard reboot command"
    },
    {
        "name": "Lowercase reboot",
        "command": "reboot",
        "description": "Lowercase variant (firmware quirk)"
    },
    {
        "name": "Sync Time",
        "command": "SYNCTIME",
        "description": "Simple non-power command"
    },
    {
        "name": "Query Attendance Logs",
        "command": "DATA QUERY ATTLOG",
        "description": "Data query command"
    },
    {
        "name": "Lock Device",
        "command": "LOCK",
        "description": "Device control command"
    },
    {
        "name": "Unlock Device",
        "command": "UNLOCK",
        "description": "Device control command"
    }
]

def queue_command(command):
    """Queue a command for the device"""
    url = f"{base_url}/{device_sn}/command"
    data = {"command": command}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"   ❌ Failed to queue command '{command}'. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Error queuing command '{command}': {e}")
        return None

def check_command_status(command_id):
    """Check the status of a queued command"""
    try:
        response = requests.get(f"{base_url}/{device_sn}/commands")
        if response.status_code == 200:
            commands = response.json()
            for cmd in commands:
                if cmd['id'] == command_id:
                    return cmd['status']
        return "unknown"
    except Exception as e:
        print(f"   Error checking command status: {e}")
        return "error"

def run_comprehensive_test():
    """Run comprehensive tests on all command formats"""
    print("🔍 ZKTeco ADMS Command Testing Suite")
    print("=" * 50)
    
    results = []
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{i+1}. Testing: {scenario['name']}")
        print(f"   Command: {scenario['command']}")
        print(f"   Description: {scenario['description']}")
        
        # Queue the command
        result = queue_command(scenario['command'])
        if not result:
            results.append({
                "name": scenario['name'],
                "command": scenario['command'],
                "status": "failed_to_queue",
                "details": "Failed to queue command"
            })
            continue
            
        command_id = result['id']
        print(f"   ✅ Command queued successfully (ID: {command_id})")
        
        # Wait and check status
        print(f"   ⏳ Waiting {check_interval} seconds to check execution status...")
        time.sleep(check_interval)
        
        status = check_command_status(command_id)
        print(f"   📊 Command status: {status}")
        
        results.append({
            "name": scenario['name'],
            "command": scenario['command'],
            "status": status,
            "command_id": command_id
        })
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    successful = 0
    failed = 0
    pending = 0
    
    for result in results:
        if result['status'] == 'completed':
            print(f"✅ {result['name']}: COMPLETED")
            successful += 1
        elif result['status'] == 'failed':
            print(f"❌ {result['name']}: FAILED")
            failed += 1
        else:
            print(f"⏳ {result['name']}: {result['status'].upper()}")
            pending += 1
    
    print(f"\n📈 Summary:")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Pending/Other: {pending}")
    
    if successful > 0:
        print(f"\n🎉 {successful} commands executed successfully!")
        print("This indicates the device can execute commands.")
    else:
        print(f"\n⚠️  No commands were executed successfully.")
        print("This suggests a device-side configuration issue.")
    
    return results

if __name__ == "__main__":
    run_comprehensive_test()