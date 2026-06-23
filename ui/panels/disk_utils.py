import customtkinter as ctk
from theme import COLORS, FONTS
from commands.disk import DiskCommands
from ui.console import Console
import threading

class DiskUtilsPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        lbl = ctk.CTkLabel(self, text="Disk Utilities", font=FONTS["title"])
        lbl.pack(pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="Logical Disks", command=lambda: self.run_cmd("logical")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Physical Disks", command=lambda: self.run_cmd("physical")).pack(side="left", padx=5)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, pady=10)

    def run_cmd(self, cmd):
        self.console.write(f"> Fetching disk info...")
        def task():
            if cmd == "logical": res = DiskCommands.get_logical_disks()
            elif cmd == "physical": res = DiskCommands.get_physical_disks()
            self.console.write(res)
        threading.Thread(target=task, daemon=True).start()
