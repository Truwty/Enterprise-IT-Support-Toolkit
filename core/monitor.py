import psutil
import time
import platform

class SystemMonitor:
    def __init__(self):
        try:
            self.last_net = psutil.net_io_counters()
        except:
            self.last_net = None
            
        try:
            self.last_disk = psutil.disk_io_counters()
        except:
            self.last_disk = None
            
        self.last_time = time.time()

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=None)

    def get_ram_usage(self):
        mem = psutil.virtual_memory()
        return {"percent": mem.percent, "free_gb": mem.free / (1024**3), "total_gb": mem.total / (1024**3)}

    def get_disk_usage(self, path=None):
        if not path:
            path = "C:\\" if platform.system() == "Windows" else "/"
        try:
            disk = psutil.disk_usage(path)
            return {"percent": disk.percent, "free_gb": disk.free / (1024**3), "total_gb": disk.total / (1024**3)}
        except:
            return {"percent": 0, "free_gb": 0, "total_gb": 0}

    def get_rates(self):
        """Calculates MB/s rates since last check for Network and Disk I/O"""
        now = time.time()
        dt = now - self.last_time
        if dt <= 0: dt = 1
        
        try:
            curr_net = psutil.net_io_counters()
        except:
            curr_net = self.last_net
            
        try:
            curr_disk = psutil.disk_io_counters()
        except:
            curr_disk = self.last_disk
            
        if curr_net and self.last_net:
            net_sent_rate = (curr_net.bytes_sent - self.last_net.bytes_sent) / dt / (1024**2)
            net_recv_rate = (curr_net.bytes_recv - self.last_net.bytes_recv) / dt / (1024**2)
        else:
            net_sent_rate = net_recv_rate = 0
            
        if curr_disk and self.last_disk:
            disk_read_rate = (curr_disk.read_bytes - self.last_disk.read_bytes) / dt / (1024**2)
            disk_write_rate = (curr_disk.write_bytes - self.last_disk.write_bytes) / dt / (1024**2)
        else:
            disk_read_rate = disk_write_rate = 0
            
        self.last_time = now
        self.last_net = curr_net
        self.last_disk = curr_disk
        
        return {
            "net_sent_mb": max(0, net_sent_rate),
            "net_recv_mb": max(0, net_recv_rate),
            "disk_read_mb": max(0, disk_read_rate),
            "disk_write_mb": max(0, disk_write_rate)
        }
