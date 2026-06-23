import customtkinter as ctk
import threading
from theme import COLORS, FONTS
from core.executor import executor
from ui.console import Console

class RemediationPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        lbl = ctk.CTkLabel(self, text="Automated Remediation Engine", font=FONTS["title"], text_color=COLORS["accent_orange"])
        lbl.pack(pady=10)

        scripts_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"])
        scripts_frame.pack(fill="x", padx=10, pady=10)

        self.scripts = {
            "Flush DNS & Renew IP": "ipconfig /flushdns; ipconfig /renew",
            "Reset Print Spooler": "Restart-Service -Name Spooler -Force",
            "Reset Windows Update Components": "net stop wuauserv; net stop cryptSvc; net stop bits; net stop msiserver; ren C:\\Windows\\SoftwareDistribution SoftwareDistribution.old; net start wuauserv; net start cryptSvc; net start bits; net start msiserver",
            "Restart Explorer.exe": "Stop-Process -Name explorer -Force",
            "Clear Temp Files": "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue",
            "Run SFC Scan (System File Checker)": "sfc /scannow"
        }

        ctk.CTkLabel(scripts_frame, text="Select Common Fault Remediation:", font=FONTS["body"]).pack(side="left", padx=15, pady=20)
        self.script_cbo = ctk.CTkComboBox(scripts_frame, values=list(self.scripts.keys()), width=300)
        self.script_cbo.pack(side="left", padx=10, pady=20)

        ctk.CTkButton(scripts_frame, text="⚡ Run Remediation", fg_color=COLORS["accent_orange"], command=self.run_remediation).pack(side="left", padx=20, pady=20)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, padx=10, pady=10)
        self.console.write("Ready. Select a script above to automatically resolve common Windows faults.")

    def run_remediation(self):
        script_name = self.script_cbo.get()
        ps_cmd = self.scripts.get(script_name)
        
        self.console.write(f"\n> Executing Automated Remediation: {script_name}")
        self.console.write(f"> Command: {ps_cmd}")
        
        def task():
            res = executor.run_powershell(ps_cmd)
            self.console.write(f"✅ Execution Complete:\n{res}")
            
        threading.Thread(target=task, daemon=True).start()
