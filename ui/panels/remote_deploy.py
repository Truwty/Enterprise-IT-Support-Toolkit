import customtkinter as ctk
from theme import COLORS, FONTS
from ui.console import Console
from core.deployment import DeploymentEngine, Machine
import os

class RemoteDeployPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.engine = DeploymentEngine()
        
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=10)
        
        lbl = ctk.CTkLabel(toolbar, text="Remote Deployment & Execution", font=FONTS["title"])
        lbl.pack(side="left", padx=5)

        ctk.CTkButton(toolbar, text="💾 Export Log", fg_color=COLORS["bg_tertiary"], width=100, command=self.export_log).pack(side="right", padx=10)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", pady=10)

        # Targets
        machine_frame = ctk.CTkFrame(top_frame, fg_color=COLORS["bg_tertiary"])
        machine_frame.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(machine_frame, text="Target IPs (One per line)").pack(pady=5)
        self.machines_text = ctk.CTkTextbox(machine_frame, height=100)
        self.machines_text.insert("end", "127.0.0.1\n")
        self.machines_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Scripts
        script_frame = ctk.CTkFrame(top_frame, fg_color=COLORS["bg_tertiary"])
        script_frame.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(script_frame, text="PowerShell / Bash Script").pack(pady=5)
        self.script_text = ctk.CTkTextbox(script_frame, height=100)
        self.script_text.insert("end", 'Write-Host "Execution success on $($env:COMPUTERNAME)"')
        self.script_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Credentials
        cred_frame = ctk.CTkFrame(top_frame, fg_color=COLORS["bg_tertiary"])
        cred_frame.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(cred_frame, text="Target Credentials").pack(pady=5)
        self.user_entry = ctk.CTkEntry(cred_frame, placeholder_text="Administrator")
        self.user_entry.pack(fill="x", padx=5, pady=5)
        self.pass_entry = ctk.CTkEntry(cred_frame, placeholder_text="Password", show="*")
        self.pass_entry.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(self, text="▶ Deploy to All Nodes", font=FONTS["heading"], fg_color=COLORS["accent_blue"], command=self.deploy).pack(pady=10)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, pady=10)
        self.console.write("System Ready. Enter target IPs, credentials, and script above.")

    def deploy(self):
        ips = self.machines_text.get("1.0", "end-1c").split("\n")
        script = self.script_text.get("1.0", "end-1c")
        usr = self.user_entry.get()
        pwd = self.pass_entry.get()

        machines = [Machine(ip.strip(), ip.strip(), usr, pwd) for ip in ips if ip.strip()]
        if not machines:
            self.console.write("! Error: No target IPs specified.")
            return
        if not script:
            self.console.write("! Error: Script body is empty.")
            return

        self.console.write(f"\n> Starting parallel deployment to {len(machines)} machines...")
        
        def log_result(res):
            status = "✅ SUCCESS" if res.success else "❌ FAILED"
            self.console.write(f"\n[{res.machine.ip}] {status} ({res.duration:.1f}s):\n{res.output.strip()}")

        # Offload to execution engine
        self.engine.deploy_script(machines, script, callback=log_result)
        
    def export_log(self):
        try:
            export_path = os.path.join(os.getcwd(), "exports", "reports", "deployment_log.txt")
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(self.console.get("1.0", "end"))
            self.console.write(f"\n✅ Execution logs exported successfully to:\n{export_path}\n")
        except Exception as e:
            self.console.write(f"\n❌ Failed to export log: {e}\n")
