import customtkinter as ctk
from theme import COLORS, FONTS
from core.sniffer import PacketSnifferEngine
from ui.console import Console

class PacketSnifferPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.engine = PacketSnifferEngine()
        
        lbl = ctk.CTkLabel(self, text="Network Packet Sniffer", font=FONTS["title"], text_color=COLORS["accent_cyan"])
        lbl.pack(pady=10)

        toolbar = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"])
        toolbar.pack(fill="x", padx=10, pady=5)
        
        self.btn_start = ctk.CTkButton(toolbar, text="▶ Start Capture", fg_color=COLORS["accent_green"], command=self.start)
        self.btn_start.pack(side="left", padx=10, pady=10)

        self.btn_stop = ctk.CTkButton(toolbar, text="⏹ Stop Capture", fg_color=COLORS["accent_red"], state="disabled", command=self.stop)
        self.btn_stop.pack(side="left", padx=10, pady=10)
        
        self.btn_export = ctk.CTkButton(toolbar, text="💾 Export PCAP", fg_color=COLORS["accent_blue"], command=self.export)
        self.btn_export.pack(side="right", padx=10, pady=10)

        self.console = Console(self)
        self.console.pack(fill="both", expand=True, padx=10, pady=10)
        self.console.write("Ready. Note: Packet sniffing requires Npcap/WinPcap on Windows, or root privileges on Linux.\n")

    def packet_callback(self, summary, error=None):
        if error:
            self.console.write(f"❌ Error: {error}")
            self.stop()
            return
        if summary:
            self.console.write(summary)
            # Auto-scroll managed by Console class

    def start(self):
        self.console.clear()
        self.console.write("Starting packet capture...\n")
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.engine.start_sniffing(self.packet_callback)

    def stop(self):
        self.engine.stop_sniffing()
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.console.write("\n⏹ Capture stopped.")

    def export(self):
        self.console.write("\n> Exporting PCAP format...")
        success, msg = self.engine.export_pcap()
        if success:
            self.console.write(f"✅ PCAP successfully saved to: {msg}")
        else:
            self.console.write(f"❌ Export Failed: {msg}")
