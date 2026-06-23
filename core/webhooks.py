import requests
from database import db

class WebhookEngine:
    @staticmethod
    def send_ticket_to_cloud(ticket_data):
        try:
            url_row = db.fetchone("SELECT value FROM settings WHERE key='webhook_url'")
            if not url_row or not url_row[0]:
                return False, "No webhook URL configured."
            
            url = url_row[0]
            
            provider_row = db.fetchone("SELECT value FROM settings WHERE key='webhook_provider'")
            provider = provider_row[0] if provider_row else "Generic"
            
            payload = {
                "source": "Enterprise IT Toolkit",
                "event": "New Ticket",
                "provider": provider,
                "ticket": ticket_data
            }
            
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code in [200, 201, 202, 204]:
                return True, f"Successfully synced to {provider}."
            else:
                return False, f"Failed with status: {res.status_code}"
        except Exception as e:
            return False, str(e)
