import customtkinter as ctk
from theme import COLORS, FONTS
from commands.system import SystemCommands
from ui.console import Console
import threading

class SystemInfoPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        lbl = ctk.CTkLabel(self, text="System Information", font=FONTS["title"])
        lbl.pack(pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="System Info", command=lambda: self.run_cmd("info")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Top Processes", command=lambda: self.run_cmd("procs")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Services", command=lambda: self.run_cmd("services")).pack(side="left", padx=5)

        kill_frame = ctk.CTkFrame(btn_frame, fg_color=COLORS["bg_tertiary"], corner_radius=8)
        kill_frame.pack(side="right", padx=15)
        
        self.pid_entry = ctk.CTkEntry(kill_frame, placeholder_text="Process ID", width=120)
        self.pid_entry.pack(side="left", padx=5, pady=5)
        ctk.CTkButton(kill_frame, text="Kill PID", fg_color=COLORS["accent_red"], width=80, command=lambda: self.run_cmd("kill")).pack(side="left", padx=5, pady=5)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, pady=10)

    def run_cmd(self, cmd):
        self.console.write(f"\n> Fetching...")
        def task():
            if cmd == "info": res = SystemCommands.get_system_info()
            elif cmd == "procs": res = SystemCommands.get_processes()
            elif cmd == "services": res = SystemCommands.get_services()
            elif cmd == "kill":
                pid = self.pid_entry.get()
                if not pid:
                    res = "❌ Please specify a valid PID to kill."
                else:
                    self.console.write(f"> Attempting to terminate PID: {pid}")
                    res = SystemCommands.kill_process(pid)
                    if not res: res = f"✅ Successfully terminated PID {pid}"
            self.console.write(res)
        threading.Thread(target=task, daemon=True).start()
