import customtkinter as ctk
import threading
import time
import platform
from theme import COLORS, FONTS
from database import db
from core.monitor import SystemMonitor
from core.alerting import alert_engine

class DashboardPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.monitor = SystemMonitor()
        self.running = True
        
        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        
        title = ctk.CTkLabel(header_frame, text="System Dashboard", font=FONTS["title"], text_color=COLORS["text_primary"])
        title.pack(side="left")
        
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        os_badge = ctk.CTkFrame(header_frame, fg_color=COLORS["bg_secondary"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        os_badge.pack(side="right", pady=5)
        ctk.CTkLabel(os_badge, text=f"💻 {os_info}", font=FONTS["small"], text_color=COLORS["text_secondary"]).pack(padx=15, pady=5)

        # --- Top KPI Cards Row ---
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.card_devices = self.create_kpi_card(self.stats_frame, "Discovered Devices", "0", COLORS["accent_cyan"], "⛤")
        self.card_devices.pack(side="left", fill="both", expand=True, padx=10)
        
        self.card_tickets = self.create_kpi_card(self.stats_frame, "Open Tickets", "0", COLORS["accent_blue"], "⚑")
        self.card_tickets.pack(side="left", fill="both", expand=True, padx=10)
        
        self.card_alerts = self.create_kpi_card(self.stats_frame, "Active Alerts", "0", COLORS["accent_red"], "⚡")
        self.card_alerts.pack(side="left", fill="both", expand=True, padx=10)

        # --- Middle Row: Real-time Telemetry ---
        self.metrics_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        self.metrics_frame.pack(fill="both", expand=True, padx=30, pady=(20, 30))
        
        metrics_header = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        metrics_header.pack(fill="x", padx=25, pady=(25, 10))
        ctk.CTkLabel(metrics_header, text="Live Host Telemetry", font=FONTS["heading"]).pack(side="left")
        ctk.CTkLabel(metrics_header, text="● Updating", font=FONTS["small"], text_color=COLORS["status_online"]).pack(side="right")
        
        self.cpu_bar, self.cpu_lbl = self.create_progress_row(self.metrics_frame, "CPU Processor Load", COLORS["accent_blue"])
        self.ram_bar, self.ram_lbl = self.create_progress_row(self.metrics_frame, "Memory (RAM) Usage", COLORS["accent_purple"])
        self.disk_bar, self.disk_lbl = self.create_progress_row(self.metrics_frame, "System Drive (C:\\)", COLORS["accent_green"])

        # --- Start Background Loops ---
        self.update_database_stats()
        self.start_live_metrics()

    def create_kpi_card(self, parent, title, value, accent_color, icon):
        # The main card
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        
        # Add an accent stripe on the left
        stripe = ctk.CTkFrame(card, fg_color=accent_color, corner_radius=12, width=6)
        stripe.pack(side="left", fill="y", pady=1)

        # Inner content
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, padx=(20, 20), pady=25)
        
        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x")
        
        # Icon inside a slight colored badge
        icon_bg = ctk.CTkFrame(header, fg_color=COLORS["bg_tertiary"], corner_radius=8, width=36, height=36)
        icon_bg.pack_propagate(False)
        icon_bg.pack(side="left")
        ctk.CTkLabel(icon_bg, text=icon, font=("Segoe UI", 18), text_color=accent_color).place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(header, text=title, font=FONTS["subheading"], text_color=COLORS["text_secondary"]).pack(side="left", padx=15)
        
        val_lbl = ctk.CTkLabel(inner, text=value, font=FONTS["metric"], text_color=COLORS["text_primary"])
        val_lbl.pack(pady=(15, 0), anchor="w")
        
        card.val_lbl = val_lbl
        return card

    def create_progress_row(self, parent, label_text, default_color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=30, pady=15)
        
        ctk.CTkLabel(row, text=label_text, width=180, anchor="w", font=FONTS["body"]).pack(side="left")
        
        bar_bg = ctk.CTkFrame(row, fg_color=COLORS["bg_primary"], corner_radius=8, height=12)
        bar_bg.pack_propagate(False)
        bar_bg.pack(side="left", fill="x", expand=True, padx=20)
        
        bar = ctk.CTkProgressBar(bar_bg, height=12, corner_radius=8, progress_color=default_color, fg_color=COLORS["bg_primary"])
        bar.place(relx=0, rely=0.5, anchor="w", relwidth=1)
        bar.set(0)
        
        lbl = ctk.CTkLabel(row, text="0%", width=70, anchor="e", font=FONTS["mono"])
        lbl.pack(side="right")
        
        return bar, lbl

    def update_database_stats(self):
        if not self.running: return
        def _fetch():
            try:
                t_res = db.fetchone("SELECT COUNT(*) FROM tickets WHERE status != 'Closed'")
                d_res = db.fetchone("SELECT COUNT(*) FROM devices")
                r_count = len(alert_engine.rules) if alert_engine.rules else 0
                
                # Safely update UI
                if self.running:
                    self.after(0, lambda: self.card_tickets.val_lbl.configure(text=str(t_res[0] if t_res else 0)))
                    self.after(0, lambda: self.card_devices.val_lbl.configure(text=str(d_res[0] if d_res else 0)))
                    self.after(0, lambda: self.card_alerts.val_lbl.configure(text=str(r_count)))
            except Exception:
                pass
            if self.running:
                self.after(5000, self.update_database_stats)
                
        threading.Thread(target=_fetch, daemon=True).start()

    def start_live_metrics(self):
        def _loop():
            while self.running:
                try:
                    cpu = self.monitor.get_cpu_usage()
                    ram = self.monitor.get_ram_usage()["percent"]
                    disk = self.monitor.get_disk_usage()["percent"]
                    if self.running:
                        self.after(0, self._render_metrics, cpu, ram, disk)
                except Exception:
                    pass
                time.sleep(1)
        threading.Thread(target=_loop, daemon=True).start()

    def _render_metrics(self, cpu, ram, disk):
        self.cpu_bar.set(cpu / 100.0)
        self.cpu_lbl.configure(text=f"{cpu:.1f}%")
        self.cpu_bar.configure(progress_color=COLORS["accent_red"] if cpu > 85 else COLORS["accent_blue"])
        
        self.ram_bar.set(ram / 100.0)
        self.ram_lbl.configure(text=f"{ram:.1f}%")
        self.ram_bar.configure(progress_color=COLORS["accent_red"] if ram > 85 else COLORS["accent_purple"])
        
        self.disk_bar.set(disk / 100.0)
        self.disk_lbl.configure(text=f"{disk:.1f}%")
        self.disk_bar.configure(progress_color=COLORS["accent_red"] if disk > 90 else COLORS["accent_green"])

    def destroy(self):
        self.running = False
        super().destroy()
