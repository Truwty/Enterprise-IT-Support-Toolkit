import customtkinter as ctk
from theme import COLORS, FONTS

class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, title, message):
        super().__init__()
        self.title(title)
        self.geometry("400x200")
        self.result = False

        lbl = ctk.CTkLabel(self, text=message, font=FONTS["body"], wraplength=350)
        lbl.pack(pady=30)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        yes_btn = ctk.CTkButton(btn_frame, text="Yes", command=self.on_yes, fg_color=COLORS["accent_red"])
        yes_btn.pack(side="left", expand=True, padx=10)

        no_btn = ctk.CTkButton(btn_frame, text="No", command=self.on_no)
        no_btn.pack(side="right", expand=True, padx=10)

        self.wait_window()

    def on_yes(self):
        self.result = True
        self.destroy()

    def on_no(self):
        self.result = False
        self.destroy()
