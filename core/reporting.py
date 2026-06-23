import os
import csv
from datetime import datetime
from database import db
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

class ComplianceReportEngine:
    @staticmethod
    def generate_csv(filepath):
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            devices = db.fetchall("SELECT ip, hostname, device_type, os_info, status, last_seen FROM devices")
            
            with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["IP Address", "Hostname", "Device Type", "OS Info", "Status", "Last Seen"])
                writer.writerows(devices)
            return True, filepath
        except Exception as e:
            return False, str(e)

    @staticmethod
    def generate_pdf(filepath):
        if not FPDF_AVAILABLE:
            return False, "FPDF2 library is missing."
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, "Enterprise IT Compliance & Inventory Report", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.ln(10)
            
            # Devices Table Header
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(40, 10, "IP Address", border=1)
            pdf.cell(50, 10, "Hostname", border=1)
            pdf.cell(30, 10, "Status", border=1)
            pdf.cell(70, 10, "Last Seen", border=1, new_x="LMARGIN", new_y="NEXT")
            
            # Data
            pdf.set_font("helvetica", "", 9)
            devices = db.fetchall("SELECT ip, hostname, status, last_seen FROM devices LIMIT 100")
            
            for dev in devices:
                pdf.cell(40, 10, str(dev[0]), border=1)
                pdf.cell(50, 10, str(dev[1])[:20], border=1)
                pdf.cell(30, 10, str(dev[2]), border=1)
                pdf.cell(70, 10, str(dev[3]), border=1, new_x="LMARGIN", new_y="NEXT")
                
            pdf.output(filepath)
            return True, filepath
        except Exception as e:
            return False, str(e)
