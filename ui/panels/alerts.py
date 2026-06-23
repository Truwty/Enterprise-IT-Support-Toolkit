import customtkinter as ctk
from theme import COLORS, FONTS
from core.alerting import alert_engine, SMTPConfig

class AlertsPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        lbl = ctk.CTkLabel(self, text="Live SMTP Alert Engine", font=FONTS["title"])
        lbl.pack(pady=10)

        smtp_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"])
        smtp_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(smtp_frame, text="SMTP Relay Configuration", font=FONTS["heading"]).pack(pady=5)
        
        form_frame = ctk.CTkFrame(smtp_frame, fg_color="transparent")
        form_frame.pack(pady=5)
        
        self.server = ctk.CTkEntry(form_frame, placeholder_text="smtp.gmail.com")
        self.server.grid(row=0, column=0, padx=5, pady=5)
        self.port = ctk.CTkEntry(form_frame, placeholder_text="587")
        self.port.grid(row=0, column=1, padx=5, pady=5)
        self.user = ctk.CTkEntry(form_frame, placeholder_text="it-alerts@domain.com")
        self.user.grid(row=0, column=2, padx=5, pady=5)
        self.pwd = ctk.CTkEntry(form_frame, placeholder_text="App Password", show="*")
        self.pwd.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkButton(smtp_frame, text="Save Config & Start Engine", command=self.save_smtp, fg_color=COLORS["accent_blue"]).pack(pady=10)

        rules_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"])
        rules_frame.pack(fill="both", expand=True, pady=10)
        ctk.CTkLabel(rules_frame, text="Active Alert Rules", font=FONTS["heading"]).pack(pady=5)
        
        self.add_rule_ui(rules_frame, "🔴 Critical CPU Spike", "cpu", 90)
        self.add_rule_ui(rules_frame, "🔴 Critical RAM Usage", "ram", 85)
        self.add_rule_ui(rules_frame, "🔴 Low Disk Space", "disk", 90)
        self.add_rule_ui(rules_frame, "🟡 Elevated CPU Load", "cpu", 70)

    def save_smtp(self):
        try:
            alert_engine.config = SMTPConfig(
                self.server.get(), int(self.port.get() or 587), 
                self.user.get(), self.pwd.get()
            )
            alert_engine.start_monitoring()
            print("Alert engine configured and actively monitoring.")
        except Exception as e:
            print(f"SMTP Configuration Error: {e}")

    def add_rule_ui(self, parent, name, metric, threshold):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"])
        card.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(card, text=f"{name} (Triggers > {threshold}%)", font=FONTS["body"]).pack(side="left", padx=10, pady=10)
        
        def toggle():
            if switch.get():
                target_email = self.user.get() or "admin@localhost"
                alert_engine.rules.append({"name": name, "metric": metric, "threshold": threshold, "target": target_email})
            else:
                alert_engine.rules = [r for r in alert_engine.rules if r['name'] != name]

        switch = ctk.CTkSwitch(card, text="Active", command=toggle)
        switch.pack(side="right", padx=10)
