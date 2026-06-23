import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
import threading
import time
from datetime import datetime
import psutil
import platform
import ctypes
from database import db

@dataclass
class SMTPConfig:
    server: str
    port: int
    username: str
    password: str

class AlertEngine:
    """Fully functional local alerting service hooking into SMTP, Desktop UI, and Sounds"""
    def __init__(self):
        self.rules = []
        self.running = False
        self.config = None

    def start_monitoring(self):
        if self.running: return
        self.running = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def stop_monitoring(self):
        self.running = False

    def _monitor_loop(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                
                for rule in self.rules:
                    if rule['metric'] == 'cpu' and cpu > rule['threshold']:
                        self._trigger_alert(rule, cpu)
                    elif rule['metric'] == 'ram' and mem > rule['threshold']:
                        self._trigger_alert(rule, mem)
                    elif rule['metric'] == 'disk' and disk > rule['threshold']:
                        self._trigger_alert(rule, disk)
            except Exception as e:
                print(f"Alert Engine Loop Error: {e}")
                
            time.sleep(10)

    def _trigger_alert(self, rule, val):
        # Anti-spam check (1 minute cooldown)
        last = rule.get('last_fired', 0)
        if time.time() - last < 60: return 
        rule['last_fired'] = time.time()
        
        print(f"ALERT TRIGGERED: {rule['name']} (Value: {val}%)")
        
        # --- Local System Notifications (Sounds & Popups) ---
        try:
            sounds = db.fetchone("SELECT value FROM settings WHERE key='enable_sounds'")
            popups = db.fetchone("SELECT value FROM settings WHERE key='enable_popups'")
            
            if sounds and str(sounds[0]) == "1":
                if platform.system() == "Windows":
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONWARNING)
                    
            if popups and str(popups[0]) == "1":
                if platform.system() == "Windows":
                    threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, f"Threshold Breached: {val}%\nRule: {rule['name']}", "Enterprise IT Toolkit - Alert", 0x30), daemon=True).start()
        except Exception as e:
            pass

        # --- Email SMTP Dispatch ---
        if not self.config or not self.config.server: 
            return
        
        msg = MIMEMultipart()
        msg['Subject'] = f"⚠️ [IT Toolkit Alert] {rule['name']} threshold breached!"
        msg['From'] = self.config.username
        msg['To'] = rule['target']
        
        body = (
            f"Automated Alert Notification\n"
            f"----------------------------\n"
            f"Rule Name: {rule['name']}\n"
            f"Current Level: {val}%\n"
            f"Trigger Threshold: {rule['threshold']}%\n"
            f"Time of Event: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(self.config.server, self.config.port) as server:
                server.starttls()
                server.login(self.config.username, self.config.password)
                server.send_message(msg)
            print("Alert email successfully dispatched.")
        except Exception as e:
            print(f"Failed to send email alert: {e}")

# Global instance
alert_engine = AlertEngine()
