import threading
import os
import logging
from datetime import datetime

# Suppress the "No libpcap provider available" warning from Scapy
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

try:
    from scapy.all import sniff, wrpcap
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

class PacketSnifferEngine:
    def __init__(self):
        self.sniffing = False
        self.packets = []
        self.thread = None

    def start_sniffing(self, packet_callback):
        if not SCAPY_AVAILABLE:
            packet_callback(None, error="Scapy or Npcap driver not installed on this system.")
            return

        self.sniffing = True
        self.packets = []
        
        def _sniff():
            try:
                # Capture packets in chunks to allow stopping gracefully
                while self.sniffing:
                    pkts = sniff(count=10, timeout=1)
                    for pkt in pkts:
                        if not self.sniffing: break
                        self.packets.append(pkt)
                        # Format a brief summary for the UI
                        summary = f"[{datetime.now().strftime('%H:%M:%S')}] {pkt.summary()}"
                        packet_callback(summary)
            except Exception as e:
                packet_callback(None, error=str(e))

        self.thread = threading.Thread(target=_sniff, daemon=True)
        self.thread.start()

    def stop_sniffing(self):
        self.sniffing = False

    def export_pcap(self, directory="exports/pcap"):
        if not SCAPY_AVAILABLE or not self.packets:
            return False, "No packets to export or missing dependencies."
        
        os.makedirs(directory, exist_ok=True)
        filename = f"capture_{datetime.now().strftime('%Y%md_%H%M%S')}.pcap"
        filepath = os.path.join(directory, filename)
        
        try:
            wrpcap(filepath, self.packets)
            return True, filepath
        except Exception as e:
            return False, str(e)
