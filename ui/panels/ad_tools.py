import customtkinter as ctk
from theme import COLORS, FONTS
from core.executor import executor
from ui.console import Console
import threading

class ADToolsPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        lbl = ctk.CTkLabel(self, text="Active Directory Integration", font=FONTS["title"], text_color=COLORS["accent_blue"])
        lbl.pack(pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="Get AD Users", command=lambda: self.run_cmd("users")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Get AD Computers", command=lambda: self.run_cmd("computers")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Check AD Connectivity", command=lambda: self.run_cmd("test")).pack(side="left", padx=5)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, pady=10)
        self.console.write("Active Directory Module Ready.\nRequires RSAT tools installed and an active domain connection.")

    def run_cmd(self, cmd):
        self.console.write(f"\n> Querying Active Directory...")
        def task():
            if cmd == "users": 
                res = executor.run_powershell("Get-ADUser -Filter * -Properties Name, Enabled, LastLogonDate | Select-Object Name, Enabled, LastLogonDate -First 20")
            elif cmd == "computers": 
                res = executor.run_powershell("Get-ADComputer -Filter * -Properties Name, OperatingSystem, IPv4Address | Select-Object Name, OperatingSystem, IPv4Address -First 20")
            elif cmd == "test":
                res = executor.run_powershell("Get-ADDomain")
                
            if not res or "The term 'Get-AD" in res:
                res = "❌ Active Directory module (RSAT) not found or not connected to a domain."
            self.console.write(res)
            
        threading.Thread(target=task, daemon=True).start()
