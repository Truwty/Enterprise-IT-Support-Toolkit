import customtkinter as ctk
from theme import COLORS, FONTS
from core.executor import executor
from ui.console import Console
import threading

class EventLogsPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        lbl = ctk.CTkLabel(self, text="Windows Event Viewer", font=FONTS["title"], text_color=COLORS["accent_blue"])
        lbl.pack(pady=10)

        ctrl_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"])
        ctrl_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(ctrl_frame, text="Log Provider:").pack(side="left", padx=(15, 5), pady=10)
        self.log_cbo = ctk.CTkComboBox(ctrl_frame, values=["System", "Application", "Security", "Setup"], width=130)
        self.log_cbo.pack(side="left", padx=5, pady=10)

        ctk.CTkLabel(ctrl_frame, text="Level:").pack(side="left", padx=(15, 5), pady=10)
        self.type_cbo = ctk.CTkComboBox(ctrl_frame, values=["Error", "Warning", "Information"], width=130)
        self.type_cbo.pack(side="left", padx=5, pady=10)

        ctk.CTkLabel(ctrl_frame, text="Max Count:").pack(side="left", padx=(15, 5), pady=10)
        self.count_entry = ctk.CTkEntry(ctrl_frame, placeholder_text="50", width=80)
        self.count_entry.pack(side="left", padx=5, pady=10)
        self.count_entry.insert(0, "50")

        ctk.CTkButton(ctrl_frame, text="🔍 Fetch Logs", fg_color=COLORS["accent_blue"], command=self.fetch_logs).pack(side="left", padx=20)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, padx=10, pady=10)
        self.console.write("Select log parameters and click Fetch.")

    def fetch_logs(self):
        log_name = self.log_cbo.get()
        log_type = self.type_cbo.get()
        count = self.count_entry.get().strip()
        if not count.isdigit(): count = "50"

        self.console.write(f"\n> Fetching latest {count} {log_type} events from {log_name} log...")
        
        def task():
            cmd = f"Get-EventLog -LogName {log_name} -EntryType {log_type} -Newest {count} | Select-Object TimeGenerated, Source, Message | Format-List"
            res = executor.run_powershell(cmd)
            if not res or "does not exist" in res:
                res = f"❌ Could not retrieve {log_name} logs. Ensure you have Administrative privileges."
            self.console.write(res)

        threading.Thread(target=task, daemon=True).start()
