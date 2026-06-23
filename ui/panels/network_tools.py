import customtkinter as ctk
from theme import COLORS, FONTS
from ui.console import Console
from commands.network import NetworkCommands
import threading

class NetworkToolsPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        lbl = ctk.CTkLabel(self, text="Network Tools", font=FONTS["title"])
        lbl.pack(pady=10)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=10)

        self.target_entry = ctk.CTkEntry(toolbar, placeholder_text="IP or Hostname")
        self.target_entry.pack(side="left", padx=10)

        ctk.CTkButton(toolbar, text="Ping", command=lambda: self.run_cmd("ping")).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="Traceroute", command=lambda: self.run_cmd("tracert")).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="IPConfig", command=lambda: self.run_cmd("ipconfig")).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="Netstat", command=lambda: self.run_cmd("netstat")).pack(side="left", padx=5)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, pady=10)

    def run_cmd(self, cmd):
        target = self.target_entry.get().strip()
        
        if cmd in ["ping", "tracert"] and not target:
            self.console.write("❌ Please enter an IP or Hostname first.")
            return
            
        self.console.write(f"\n> Running {cmd} {target}...")
        
        def task():
            if cmd == "ping":
                res = NetworkCommands.ping(target)
            elif cmd == "tracert":
                res = NetworkCommands.tracert(target)
            elif cmd == "ipconfig":
                res = NetworkCommands.get_ipconfig()
            elif cmd == "netstat":
                res = NetworkCommands.get_netstat()
            else:
                res = "Unknown command"
            self.console.write(res)
            
        threading.Thread(target=task, daemon=True).start()
