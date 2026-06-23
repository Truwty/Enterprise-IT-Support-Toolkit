import customtkinter as ctk
from theme import COLORS, FONTS
from database import db
from datetime import datetime

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        ctk.CTkLabel(header_frame, text="Toolkit Configuration", font=FONTS["title"], text_color=COLORS["text_primary"]).pack(side="left")

        # Tabview for organizing settings
        self.tabview = ctk.CTkTabview(
            self, 
            fg_color=COLORS["bg_secondary"],
            segmented_button_fg_color=COLORS["bg_tertiary"],
            segmented_button_selected_color=COLORS["accent_blue"],
            segmented_button_selected_hover_color=COLORS["accent_cyan"],
            segmented_button_unselected_color=COLORS["bg_tertiary"],
            corner_radius=12
        )
        self.tabview.pack(fill="both", expand=True, padx=30, pady=10)

        # Tabs Setup
        self.tabs = {}
        for tab_name in ["General Appearance", "Network & Remote", "Monitoring & Alerts", "System & Logs", "Cloud Webhooks"]:
            self.tabview.add(tab_name)
            sf = ctk.CTkScrollableFrame(self.tabview.tab(tab_name), fg_color="transparent")
            sf.pack(fill="both", expand=True, padx=5, pady=5)
            self.tabs[tab_name] = sf

        self.widgets = {}
        
        # Populate Tabs
        self._setup_appearance_tab(self.tabs["General Appearance"])
        self._setup_network_tab(self.tabs["Network & Remote"])
        self._setup_monitoring_tab(self.tabs["Monitoring & Alerts"])
        self._setup_system_tab(self.tabs["System & Logs"])
        self._setup_webhooks_tab(self.tabs["Cloud Webhooks"])

        # Bottom Actions
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=(10, 30))

        self.status_lbl = ctk.CTkLabel(action_frame, text="", font=FONTS["body"], text_color=COLORS["accent_green"])
        self.status_lbl.pack(side="left", padx=10)

        ctk.CTkButton(action_frame, text="↺ Reset Defaults", fg_color=COLORS["bg_tertiary"], hover_color=COLORS["bg_hover"], text_color=COLORS["text_primary"], command=self.reset_defaults).pack(side="right", padx=10)
        ctk.CTkButton(action_frame, text="💾 Save Settings", fg_color=COLORS["accent_blue"], hover_color=COLORS["accent_cyan"], font=FONTS["heading"], command=self.save_settings).pack(side="right", padx=10)

        # Initialize Default Map & Load
        self.default_settings = {
            "theme_mode": "Dark",
            "ui_scaling": "100%",
            "default_subnet": "192.168.1.0/24",
            "scan_timeout_ms": "500",
            "max_threads": "50",
            "remote_method": "WinRM",
            "winrm_port": "5985",
            "ssh_port": "22",
            "graph_refresh_s": "1 Second",
            "cpu_alert_pct": "90",
            "ram_alert_pct": "85",
            "disk_alert_pct": "10",
            "enable_logs": "1",
            "log_retention_days": "30",
            "enable_sounds": "0",
            "enable_popups": "1"
        }
        
        self.load_settings()

    def _setup_appearance_tab(self, parent):
        self._create_section_label(parent, "UI Preferences")
        self._create_setting_row(parent, "Theme Mode", "theme_mode", "combo", values=["Dark", "Light", "System"])
        self._create_setting_row(parent, "UI Scaling", "ui_scaling", "combo", values=["80%", "90%", "100%", "110%", "120%"])
        
    def _setup_network_tab(self, parent):
        self._create_section_label(parent, "Scanner Configuration")
        self._create_setting_row(parent, "Default Subnet", "default_subnet", "entry", placeholder_text="e.g. 192.168.1.0/24")
        self._create_setting_row(parent, "Ping Timeout (ms)", "scan_timeout_ms", "entry")
        self._create_setting_row(parent, "Max Concurrent Threads", "max_threads", "entry")
        
        self._create_section_label(parent, "Remote Execution")
        self._create_setting_row(parent, "Default Protocol", "remote_method", "combo", values=["WinRM", "SSH", "Local Subprocess"])
        self._create_setting_row(parent, "WinRM Port", "winrm_port", "entry")
        self._create_setting_row(parent, "SSH Port", "ssh_port", "entry")

    def _setup_monitoring_tab(self, parent):
        self._create_section_label(parent, "Telemetry Graphs")
        self._create_setting_row(parent, "Graph Refresh Rate", "graph_refresh_s", "combo", values=["1 Second", "2 Seconds", "5 Seconds"])
        
        self._create_section_label(parent, "Alert Thresholds")
        self._create_setting_row(parent, "CPU Critical Threshold (%)", "cpu_alert_pct", "entry")
        self._create_setting_row(parent, "RAM Critical Threshold (%)", "ram_alert_pct", "entry")
        self._create_setting_row(parent, "Disk Free Warning (%)", "disk_alert_pct", "entry")

    def _setup_system_tab(self, parent):
        self._create_section_label(parent, "Logging")
        self._create_setting_row(parent, "Enable File Logging", "enable_logs", "switch")
        self._create_setting_row(parent, "Log Retention (Days)", "log_retention_days", "entry")
        
        self._create_section_label(parent, "Notifications")
        self._create_setting_row(parent, "Enable Sound Alerts", "enable_sounds", "switch")
        self._create_setting_row(parent, "Enable Desktop Popups", "enable_popups", "switch")

    def _setup_webhooks_tab(self, parent):
        self._create_section_label(parent, "Helpdesk API Integrations")
        self._create_setting_row(parent, "Provider", "webhook_provider", "combo", values=["ServiceNow", "Jira", "Zendesk", "Generic Slack/Teams"])
        self._create_setting_row(parent, "Webhook URL / API Endpoint", "webhook_url", "entry", placeholder_text="https://...")

    def _create_section_label(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text, font=FONTS["subheading"], text_color=COLORS["accent_blue"], anchor="w")
        lbl.pack(fill="x", padx=10, pady=(20, 5))
        line = ctk.CTkFrame(parent, fg_color=COLORS["border"], height=1)
        line.pack(fill="x", padx=10, pady=(0, 10))

    def _create_setting_row(self, parent, label_text, key, widget_type="entry", **kwargs):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=8, padx=20)
        
        ctk.CTkLabel(row, text=label_text, font=FONTS["body"], text_color=COLORS["text_primary"]).pack(side="left")
        
        if widget_type == "entry":
            w = ctk.CTkEntry(row, width=200, fg_color=COLORS["bg_tertiary"], border_color=COLORS["border"], **kwargs)
        elif widget_type == "combo":
            w = ctk.CTkComboBox(row, width=200, fg_color=COLORS["bg_tertiary"], border_color=COLORS["border"], button_color=COLORS["accent_blue"], **kwargs)
        elif widget_type == "switch":
            w = ctk.CTkSwitch(row, text="", width=50, progress_color=COLORS["accent_green"])
            
        w.pack(side="right")
        self.widgets[key] = (w, widget_type)

    def load_settings(self):
        # Fetch DB Settings
        db_settings = {}
        try:
            rows = db.fetchall("SELECT key, value FROM settings")
            for k, v in rows:
                db_settings[k] = v
        except Exception:
            pass

        # Apply to Widgets
        for key, (widget, w_type) in self.widgets.items():
            val = db_settings.get(key, self.default_settings.get(key, ""))
            
            if w_type == "entry":
                widget.delete(0, "end")
                widget.insert(0, val)
            elif w_type == "combo":
                widget.set(val)
            elif w_type == "switch":
                if str(val) == "1":
                    widget.select()
                else:
                    widget.deselect()

    def save_settings(self):
        try:
            for key, (widget, w_type) in self.widgets.items():
                if w_type == "entry":
                    val = widget.get()
                elif w_type == "combo":
                    val = widget.get()
                elif w_type == "switch":
                    val = "1" if widget.get() else "0"
                
                # UPSERT
                db.execute(
                    """
                    INSERT INTO settings (key, value, updated_at) 
                    VALUES (?, ?, ?) 
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                    """, 
                    (key, str(val), datetime.now().isoformat())
                )
            
            # Apply immediate UI changes if applicable
            theme_val = self.widgets["theme_mode"][0].get()
            if theme_val in ["Dark", "Light", "System"]:
                current_mode = ctk.get_appearance_mode()
                if current_mode != theme_val:
                    ctk.set_appearance_mode(theme_val)
                    self.show_status("✅ Settings saved! (Please restart the app to sync custom graphs)", color=COLORS["accent_green"])
                    return

            self.show_status("✅ Settings saved successfully!")
        except Exception as e:
            self.show_status(f"❌ Error saving: {e}", color=COLORS["accent_red"])

    def reset_defaults(self):
        for key, (widget, w_type) in self.widgets.items():
            val = self.default_settings.get(key, "")
            if w_type == "entry":
                widget.delete(0, "end")
                widget.insert(0, val)
            elif w_type == "combo":
                widget.set(val)
            elif w_type == "switch":
                if str(val) == "1":
                    widget.select()
                else:
                    widget.deselect()
        self.show_status("↺ Defaults restored (Unsaved)", color=COLORS["accent_orange"])

    def show_status(self, text, color=COLORS["accent_green"]):
        self.status_lbl.configure(text=text, text_color=color)
        self.after(5000, lambda: self.status_lbl.configure(text=""))
