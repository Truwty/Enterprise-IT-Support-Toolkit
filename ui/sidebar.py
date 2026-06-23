import customtkinter as ctk
from theme import COLORS, FONTS

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, command=None):
        super().__init__(master, fg_color=COLORS["bg_secondary"], corner_radius=0, width=240)
        self.pack_propagate(False)
        self.command = command

        # Right border accent line
        accent_line = ctk.CTkFrame(self, fg_color=COLORS["border"], width=1, corner_radius=0)
        accent_line.place(relx=1, rely=0, anchor="ne", relheight=1)

        self.buttons = {}
        
        # Categorized menu items for better visual pacing
        menu_sections = [
            ("MAIN", [
                ("Dashboard", "dashboard", "⊞"),
                ("Graphs", "graphs", "∿"),
            ]),
            ("NETWORK", [
                ("Network Tools", "network_tools", "⚄"),
                ("Topology", "topology", "⛤"),
                ("Packet Sniffer", "packet_sniffer", "∿"),
            ]),
            ("MANAGEMENT", [
                ("Remote Deploy", "deploy", "⚡"),
                ("Alert Engine", "alerts", "✉"),
                ("Ticketing", "tickets", "⚑"),
                ("Active Directory", "ad_tools", "👥"),
                ("Azure AD / Intune", "azure_tools", "☁"),
            ]),
            ("LOCAL SYSTEM", [
                ("System Info", "system_info", "⚙"),
                ("Remediation", "remediation", "🔧"),
                ("Disk Utils", "disk_utils", "⛁"),
                ("Event Logs", "event_logs", "☰"),
                ("Admin Tools", "admin_tools", "⚿"),
            ]),
            ("PREFERENCES", [
                ("Compliance Reports", "reporting", "📄"),
                ("Settings", "settings", "⛭"),
            ])
        ]

        # Build UI
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for section_title, items in menu_sections:
            lbl = ctk.CTkLabel(scroll_frame, text=section_title, font=("Segoe UI", 10, "bold"), text_color=COLORS["text_disabled"], anchor="w")
            lbl.pack(fill="x", padx=10, pady=(15, 5))

            for label, name, icon in items:
                btn = ctk.CTkButton(
                    scroll_frame, 
                    text=f"  {icon}   {label}", 
                    font=FONTS["body"],
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    hover_color=COLORS["bg_hover"],
                    anchor="w",
                    height=36,
                    corner_radius=8,
                    command=lambda n=name: self._on_click(n)
                )
                btn.pack(fill="x", padx=5, pady=2)
                self.buttons[name] = btn

    def _on_click(self, name):
        # Reset all buttons
        for btn in self.buttons.values():
            btn.configure(fg_color="transparent", text_color=COLORS["text_secondary"])
            
        # Highlight active button
        self.buttons[name].configure(fg_color=COLORS["bg_tertiary"], text_color=COLORS["text_primary"])
        
        if self.command:
            self.command(name)
