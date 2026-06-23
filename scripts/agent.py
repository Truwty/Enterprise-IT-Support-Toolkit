import psutil
import requests
import time
import socket
import platform
import argparse

def run_agent(server_url):
    print(f"[*] Starting Enterprise IT Persistent Telemetry Agent")
    print(f"[*] Target Endpoint: {server_url}")
    while True:
        try:
            payload = {
                "hostname": socket.gethostname(),
                "os": platform.system(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "ram_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "timestamp": time.time()
            }
            res = requests.post(server_url, json=payload, timeout=5)
            print(f"[+] Synced telemetry. Response: {res.status_code}")
        except Exception as e:
            print(f"[-] Sync failed: {e}")
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Persistent Remote Telemetry Agent")
    parser.add_argument("--url", type=str, default="http://192.168.1.100:8080/api/telemetry", help="Target webhook/API URL for telemetry")
    args = parser.parse_args()
    run_agent(args.url)
