import customtkinter as ctk
import sys
import threading
from database import db
from core.alerting import alert_engine
from ui.header import Header
from ui.sidebar import Sidebar
from ui.statusbar import StatusBar
from theme import COLORS

# Pre-initialize theme from DB before rendering panels
try:
    theme_setting = db.fetchone("SELECT value FROM settings WHERE key='theme_mode'")
    if theme_setting:
        ctk.set_appearance_mode(theme_setting[0])
    else:
        ctk.set_appearance_mode("Dark")
except:
    ctk.set_appearance_mode("Dark")

ctk.set_default_color_theme("blue")

# Import all panels AFTER theme load
from ui.panels.dashboard import DashboardPanel
from ui.panels.topology import TopologyPanel
from ui.panels.performance import PerformancePanel
from ui.panels.remote_deploy import RemoteDeployPanel
from ui.panels.alerts import AlertsPanel
from ui.panels.settings import SettingsPanel
from ui.panels.network_tools import NetworkToolsPanel
from ui.panels.system_info import SystemInfoPanel
from ui.panels.disk_utils import DiskUtilsPanel
from ui.panels.event_logs import EventLogsPanel
from ui.panels.tickets import TicketsPanel
from ui.panels.admin_tools import AdminToolsPanel
from ui.panels.ad_tools import ADToolsPanel
from ui.panels.azure_tools import AzureToolsPanel
from ui.panels.remediation import RemediationPanel
from ui.panels.packet_sniffer import PacketSnifferPanel
from ui.panels.reporting import ReportingPanel

class ITToolkitApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Enterprise IT Toolkit v3.0")
        self.geometry("1400x900")
        self.configure(fg_color=COLORS["bg_primary"])

        # Window Fade-In Setup
        self.attributes("-alpha", 0.0)

        # Grid layout (Header, Content, StatusBar)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Header
        self.header = Header(self)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Sidebar
        self.sidebar = Sidebar(self, command=self.switch_panel)
        self.sidebar.grid(row=1, column=0, sticky="ns")

        # Main Content Area
        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Panels
        self.panels = {}
        self.current_panel = None
        self.is_animating = False

        self._init_panels()

        # Status Bar
        self.statusbar = StatusBar(self)
        self.statusbar.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Override close behavior for fade-out
        self.protocol("WM_DELETE_WINDOW", self.fade_out_and_close)

        # Select Dashboard by default instantly (no slide for first load)
        self.current_panel = "dashboard"
        self.panels["dashboard"].place(relx=0, rely=0, relwidth=1, relheight=1)
        self.statusbar.set_status("Ready")
        
        # Trigger fade-in
        self.after(100, self.fade_in)

    def fade_in(self, current_alpha=0.0):
        current_alpha += 0.05
        if current_alpha >= 1.0:
            self.attributes("-alpha", 1.0)
            return
        self.attributes("-alpha", current_alpha)
        self.after(16, self.fade_in, current_alpha)

    def fade_out_and_close(self, current_alpha=1.0):
        current_alpha -= 0.08
        if current_alpha <= 0.0:
            self.attributes("-alpha", 0.0)
            
            # Clean up background daemons and resources to prevent hanging threads
            try:
                alert_engine.stop_monitoring()
                db.close()
                for panel in self.panels.values():
                    panel.destroy()
            except Exception:
                pass
                
            self.destroy()
            sys.exit(0)
            return
        self.attributes("-alpha", current_alpha)
        self.after(16, self.fade_out_and_close, current_alpha)

    def _init_panels(self):
        self.panels["dashboard"] = DashboardPanel(self.content_frame)
        self.panels["network_tools"] = NetworkToolsPanel(self.content_frame)
        self.panels["topology"] = TopologyPanel(self.content_frame)
        self.panels["graphs"] = PerformancePanel(self.content_frame)
        self.panels["deploy"] = RemoteDeployPanel(self.content_frame)
        self.panels["alerts"] = AlertsPanel(self.content_frame)
        self.panels["system_info"] = SystemInfoPanel(self.content_frame)
        self.panels["disk_utils"] = DiskUtilsPanel(self.content_frame)
        self.panels["event_logs"] = EventLogsPanel(self.content_frame)
        self.panels["tickets"] = TicketsPanel(self.content_frame)
        self.panels["ad_tools"] = ADToolsPanel(self.content_frame)
        self.panels["azure_tools"] = AzureToolsPanel(self.content_frame)
        self.panels["remediation"] = RemediationPanel(self.content_frame)
        self.panels["packet_sniffer"] = PacketSnifferPanel(self.content_frame)
        self.panels["reporting"] = ReportingPanel(self.content_frame)
        self.panels["admin_tools"] = AdminToolsPanel(self.content_frame)
        self.panels["settings"] = SettingsPanel(self.content_frame)

    def switch_panel(self, panel_name):
        if panel_name not in self.panels:
            print(f"Warning: Panel '{panel_name}' is not registered.")
            return
            
        if self.is_animating or panel_name == self.current_panel:
            return

        old_panel = self.panels[self.current_panel] if self.current_panel else None
        new_panel = self.panels[panel_name]
        self.current_panel = panel_name

        self.statusbar.set_status(f"Switched to {panel_name.replace('_', ' ').title()}")
        self.animate_transition(old_panel, new_panel)

    def animate_transition(self, old_p, new_p, step=0.0):
        self.is_animating = True
        
        if step >= 1.0:
            if old_p: 
                old_p.place_forget()
            new_p.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.is_animating = False
            return
            
        # Ease-out cubic curve calculation for buttery smooth slowing down
        t = 1 - pow(1 - step, 3)
        
        # Slide old out to the left, new in from the right
        if old_p:
            old_p.place(relx=-t, rely=0, relwidth=1, relheight=1)
        
        new_p.place(relx=1-t, rely=0, relwidth=1, relheight=1)
        
        # 60fps pacing (~16ms). Increment controls speed.
        self.after(16, self.animate_transition, old_p, new_p, step + 0.06)
