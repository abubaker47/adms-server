#!/usr/bin/env python3
import socket
import sys

def test_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"✅ Port {port} is OPEN on {host}")
            return True
        else:
            print(f"❌ Port {port} is CLOSED on {host}")
            return False
    except Exception as e:
        print(f"❌ Error testing {host}:{port} - {e}")
        return False

if __name__ == "__main__":
    host = "128.199.24.193"
    port = 8080
    print(f"Testing connectivity to {host}:{port}...")
    test_port(host, port)
