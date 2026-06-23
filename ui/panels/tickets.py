import customtkinter as ctk
from theme import COLORS, FONTS
from database import db
from datetime import datetime
import threading
from core.webhooks import WebhookEngine

class TicketsPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        lbl = ctk.CTkLabel(self, text="Helpdesk Ticketing System", font=FONTS["title"])
        lbl.pack(pady=10)

        # Form to create ticket
        form_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_tertiary"])
        form_frame.pack(fill="x", padx=10, pady=10)

        self.title_entry = ctk.CTkEntry(form_frame, placeholder_text="Ticket Title / Subject", width=300)
        self.title_entry.pack(side="left", padx=10, pady=10)

        self.desc_entry = ctk.CTkEntry(form_frame, placeholder_text="Detailed Description of the Issue", width=400)
        self.desc_entry.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(form_frame, text="Create Ticket", fg_color=COLORS["accent_blue"], command=self.create_ticket).pack(side="left", padx=10)

        # List of tickets
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_secondary"])
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_tickets()

    def create_ticket(self):
        t_title = self.title_entry.get()
        t_desc = self.desc_entry.get()
        if not t_title: return

        # Generate unique ticket number based on unix timestamp
        t_num = f"TKT-{int(datetime.now().timestamp())}"
        
        # Insert to SQLite DB instance
        db.execute(
            "INSERT INTO tickets (ticket_number, title, description, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (t_num, t_title, t_desc, "Open", datetime.now().isoformat())
        )
        
        # Clear forms
        self.title_entry.delete(0, 'end')
        self.desc_entry.delete(0, 'end')
        
        # Refresh UI
        self.load_tickets()
        
        # Trigger Webhook Sync in background
        threading.Thread(target=self.sync_webhook, args=(t_num, t_title, t_desc), daemon=True).start()

    def sync_webhook(self, t_num, title, desc):
        success, msg = WebhookEngine.send_ticket_to_cloud({"id": t_num, "title": title, "desc": desc})
        print(f"Webhook Sync -> {msg}")

    def close_ticket(self, t_num):
        db.execute("UPDATE tickets SET status = 'Closed' WHERE ticket_number = ?", (t_num,))
        self.load_tickets()

    def load_tickets(self):
        # Clear existing
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        # Fetch from SQLite DB
        tickets = db.fetchall("SELECT ticket_number, title, status, description, created_at FROM tickets ORDER BY id DESC")
        
        if not tickets:
            ctk.CTkLabel(self.list_frame, text="No tickets exist in the database.", text_color=COLORS["text_disabled"]).pack(pady=20)
            return

        for tkt in tickets:
            t_num, t_title, t_stat, t_desc, t_date = tkt
            
            card = ctk.CTkFrame(self.list_frame, fg_color=COLORS["bg_tertiary"])
            card.pack(fill="x", pady=5, padx=5)
            
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(10,0))
            
            ctk.CTkLabel(header, text=f"{t_num} — {t_title}", font=FONTS["heading"]).pack(side="left")
            
            color = COLORS["accent_green"] if t_stat == "Closed" else COLORS["accent_orange"]
            ctk.CTkLabel(header, text=t_stat, text_color=color, font=FONTS["badge"]).pack(side="right")
            
            ctk.CTkLabel(card, text=t_desc, text_color=COLORS["text_secondary"], justify="left").pack(anchor="w", padx=10, pady=5)
            
            if t_stat != "Closed":
                ctk.CTkButton(card, text="Mark Closed", width=100, height=24, fg_color=COLORS["border"], hover_color=COLORS["accent_red"], command=lambda n=t_num: self.close_ticket(n)).pack(anchor="e", padx=10, pady=(0,10))
