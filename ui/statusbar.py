import customtkinter as ctk
from theme import COLORS, FONTS

class StatusBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg_secondary"], corner_radius=0, height=30)
        self.pack_propagate(False)

        self.status_lbl = ctk.CTkLabel(self, text="● Ready", font=FONTS["small"], text_color=COLORS["status_online"])
        self.status_lbl.pack(side="left", padx=10)

        self.info_lbl = ctk.CTkLabel(self, text="|  Elapsed: 0.00s", font=FONTS["small"], text_color=COLORS["text_secondary"])
        self.info_lbl.pack(side="left", padx=10)

    def set_status(self, text, color=COLORS["text_primary"]):
        self.status_lbl.configure(text=f"● {text}", text_color=color)
