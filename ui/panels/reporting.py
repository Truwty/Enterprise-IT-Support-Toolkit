import customtkinter as ctk
import threading
from theme import COLORS, FONTS
from core.reporting import ComplianceReportEngine
from ui.console import Console

class ReportingPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        lbl = ctk.CTkLabel(self, text="Compliance & Reporting", font=FONTS["title"], text_color=COLORS["accent_purple"])
        lbl.pack(pady=10)

        form_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"])
        form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Report Type:", font=FONTS["body"]).grid(row=0, column=0, padx=10, pady=15)
        self.type_cbo = ctk.CTkComboBox(form_frame, values=["Hardware & Asset Inventory", "Active Alert History", "Ticket Compliance"])
        self.type_cbo.grid(row=0, column=1, padx=10, pady=15)

        ctk.CTkLabel(form_frame, text="Format:", font=FONTS["body"]).grid(row=0, column=2, padx=10, pady=15)
        self.format_cbo = ctk.CTkComboBox(form_frame, values=["PDF Document", "CSV Spreadsheet"])
        self.format_cbo.grid(row=0, column=3, padx=10, pady=15)

        ctk.CTkButton(form_frame, text="⚙️ Generate Report", fg_color=COLORS["accent_blue"], command=self.generate).grid(row=0, column=4, padx=20, pady=15)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, padx=10, pady=10)

    def generate(self):
        fmt = self.format_cbo.get()
        rep_type = self.type_cbo.get()
        self.console.write(f"> Generating {rep_type} as {fmt}...")
        
        def task():
            if "PDF" in fmt:
                path = f"exports/reports/Compliance_{rep_type.replace(' ', '')}.pdf"
                success, msg = ComplianceReportEngine.generate_pdf(path)
            else:
                path = f"exports/reports/Compliance_{rep_type.replace(' ', '')}.csv"
                success, msg = ComplianceReportEngine.generate_csv(path)
                
            if success:
                self.console.write(f"✅ Successfully generated report at:\n{msg}")
            else:
                self.console.write(f"❌ Failed to generate report:\n{msg}")
                
        threading.Thread(target=task, daemon=True).start()
