import customtkinter as ctk
from theme import COLORS, FONTS
from core.executor import executor
from ui.console import Console
import threading

class AdminToolsPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        lbl = ctk.CTkLabel(self, text="Local Admin Tools", font=FONTS["title"], text_color=COLORS["accent_purple"])
        lbl.pack(pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"])
        btn_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(btn_frame, text="List Local Users", command=lambda: self.run_cmd("users")).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="List Local Groups", command=lambda: self.run_cmd("groups")).pack(side="left", padx=10, pady=10)

        act_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"])
        act_frame.pack(fill="x", padx=10, pady=10)

        self.user_entry = ctk.CTkEntry(act_frame, placeholder_text="Username", width=200)
        self.user_entry.pack(side="left", padx=10, pady=10)
        ctk.CTkButton(act_frame, text="Get User Info", fg_color=COLORS["accent_blue"], command=lambda: self.run_cmd("user_info")).pack(side="left", padx=10)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, padx=10, pady=10)
        self.console.write("Local Security Authority (SAM) Querying Tools.")

    def run_cmd(self, cmd):
        def task():
            if cmd == "users": 
                self.console.write("\n> Fetching local users...")
                res = executor.run_powershell("Get-LocalUser | Select-Object Name, Enabled, Description | Format-Table")
            elif cmd == "groups": 
                self.console.write("\n> Fetching local groups...")
                res = executor.run_powershell("Get-LocalGroup | Select-Object Name, Description | Format-Table")
            elif cmd == "user_info":
                usr = self.user_entry.get().strip()
                if not usr:
                    self.console.write("\n❌ Please specify a username.")
                    return
                self.console.write(f"\n> Fetching details for user: {usr}...")
                res = executor.run_powershell(f"Get-LocalUser -Name '{usr}' | Format-List *")
            
            if not res:
                res = "Command returned empty output."
            self.console.write(res)
            
        threading.Thread(target=task, daemon=True).start()
