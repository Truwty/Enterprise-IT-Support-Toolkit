import customtkinter as ctk
from theme import COLORS, FONTS
from logger import log
from database import db

class Console(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, font=FONTS["mono"], fg_color=COLORS["bg_tertiary"], text_color=COLORS["text_primary"], **kwargs)

    def write(self, text):
        clean_text = text.strip()
        self.insert("end", clean_text + "\n")
        self.see("end")
        
        try:
            res = db.fetchone("SELECT value FROM settings WHERE key='enable_logs'")
            if res and str(res[0]) == "1":
                log.info(clean_text)
        except Exception:
            pass

    def clear(self):
        self.delete("0.0", "end")
