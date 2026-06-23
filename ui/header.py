import customtkinter as ctk
from theme import COLORS, FONTS
import getpass
from datetime import datetime

class Header(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg_secondary"], corner_radius=0, height=70)
        self.pack_propagate(False)

        # Bottom border accent line
        accent_line = ctk.CTkFrame(self, fg_color=COLORS["border"], height=1, corner_radius=0)
        accent_line.place(relx=0, rely=1, anchor="sw", relwidth=1)

        # Left side
        logo_lbl = ctk.CTkLabel(self, text="⚡", font=("Segoe UI", 28))
        logo_lbl.pack(side="left", padx=(25, 5), pady=15)

        title = ctk.CTkLabel(self, text="Enterprise IT Toolkit", font=("Segoe UI", 20, "bold"), text_color=COLORS["text_primary"])
        title.pack(side="left", padx=5, pady=15)

        admin_badge = ctk.CTkFrame(self, fg_color=COLORS["accent_blue"], corner_radius=6, height=24)
        admin_badge.pack_propagate(False)
        admin_badge.pack(side="left", padx=15, pady=23)
        ctk.CTkLabel(admin_badge, text="ADMIN", font=("Segoe UI", 10, "bold"), text_color="#ffffff").pack(padx=8, pady=2)

        # Right side
        user_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"], corner_radius=8, height=36)
        user_frame.pack_propagate(False)
        user_frame.pack(side="right", padx=25, pady=17)
        
        user_info = f"👤 {getpass.getuser()}"
        ctk.CTkLabel(user_frame, text=user_info, font=FONTS["body"], text_color=COLORS["text_primary"]).pack(padx=15, pady=6)

        self.time_lbl = ctk.CTkLabel(self, text="", font=FONTS["mono"], text_color=COLORS["text_secondary"])
        self.time_lbl.pack(side="right", padx=15, pady=15)

        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_lbl.configure(text=current_time)
        self.after(1000, self.update_time)
