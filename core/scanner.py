import socket
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
import ipaddress
import time

@dataclass
class Device:
    ip: str
    hostname: str
    mac: str
    device_type: str
    status: str
    open_ports: list[int]
    os_info: str
    response_time: float
    last_seen: datetime
    x: float = 0.0
    y: float = 0.0
    details: dict = field(default_factory=dict)

class NetworkScanner:
    """Full functional network discovery engine."""
    
    def scan_subnet(self, subnet: str) -> list[Device]:
        try:
            network = ipaddress.ip_network(subnet, strict=False)
        except ValueError:
            return []
        
        devices = []
        with ThreadPoolExecutor(max_workers=100) as executor:
            # We only scan first 254 hosts to keep it fast
            hosts_to_scan = list(network.hosts())[:254]
            futures = [executor.submit(self._scan_ip, str(ip)) for ip in hosts_to_scan]
            for f in futures:
                res = f.result()
                if res:
                    devices.append(res)
        return devices

    def _scan_ip(self, ip: str) -> Device:
        start = time.time()
        if self.ping_host(ip):
            rt = round((time.time() - start) * 1000, 2)
            hostname = self.get_hostname(ip)
            ports = self.get_open_ports(ip, [22, 80, 443, 445, 3389, 9100])
            
            dtype = "unknown"
            if 9100 in ports: dtype = "printer"
            elif 3389 in ports: dtype = "workstation"
            elif 445 in ports: dtype = "server"
            elif 22 in ports: dtype = "router"
            elif 80 in ports or 443 in ports: dtype = "switch"
            
            return Device(ip, hostname, "Unknown", dtype, "online", ports, "Unknown OS", rt, datetime.now())
        return None

    def ping_host(self, ip: str) -> bool:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        timeout = '-w' if platform.system().lower() == 'windows' else '-W'
        cmd = ['ping', param, '1', timeout, '1' if timeout == '-W' else '500', ip]
        try:
            return subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        except Exception:
            return False

    def get_hostname(self, ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "Unknown"

    def get_open_ports(self, ip: str, ports: list) -> list[int]:
        open_ports = []
        for port in ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.3)
                    if s.connect_ex((ip, port)) == 0:
                        open_ports.append(port)
            except Exception:
                pass
        return open_ports
