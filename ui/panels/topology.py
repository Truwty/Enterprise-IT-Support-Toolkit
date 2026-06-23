import customtkinter as ctk
import tkinter as tk
from PIL import ImageGrab
from theme import COLORS, FONTS, get_color
import threading
import networkx as nx
from core.scanner import NetworkScanner
from core.executor import executor
import os
import time
import math

DEVICE_ICONS = {
    "router": "🖧",
    "switch": "⛫",
    "server": "🗄",
    "workstation": "💻",
    "printer": "🖨",
    "unknown": "❓"
}

class QuickDiag(ctk.CTkToplevel):
    """Floating diagnostic console for right-click node actions."""
    def __init__(self, master, title_text, ip, action):
        super().__init__(master)
        self.title(title_text)
        self.geometry("650x450")
        self.attributes("-topmost", True)
        self.configure(fg_color=COLORS["bg_primary"])
        
        # Color coding for dangerous actions
        text_col = COLORS["accent_red"] if action in ["block", "shutdown"] else COLORS["accent_blue"]
        
        lbl = ctk.CTkLabel(self, text=f"Executing: {title_text} [{ip}]", font=FONTS["heading"], text_color=text_col)
        lbl.pack(pady=10)
        
        self.textbox = ctk.CTkTextbox(self, font=FONTS["mono"], fg_color=COLORS["bg_tertiary"], text_color=COLORS["text_primary"])
        self.textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.ip = ip
        self.action = action
        threading.Thread(target=self.run_task, daemon=True).start()
        
    def run_task(self):
        self.write(f"> Initializing {self.action} on {self.ip}...\n")
        if self.action == "ping":
            res = executor.run_powershell(f"ping -n 4 {self.ip}")
        elif self.action == "tracert":
            res = executor.run_powershell(f"tracert -d -w 500 {self.ip}")
        elif self.action == "scan":
            self.write("> Testing common enterprise ports...\n")
            res = executor.run_powershell(f'22,80,443,445,3389,9100 | % {{ try {{ $t=New-Object System.Net.Sockets.TcpClient; $t.ConnectAsync("{self.ip}", $_).Wait(500); if($t.Connected){{ "$_ is OPEN" }}; $t.Close() }} catch {{}} }}')
            if not res.strip(): res = "No standard ports open."
        elif self.action == "block":
            self.write("> Injecting Windows Firewall block rules for inbound/outbound traffic...\n")
            cmd = f'New-NetFirewallRule -DisplayName "IT Toolkit Block {self.ip}" -Direction Inbound -Action Block -RemoteAddress {self.ip}; ' \
                  f'New-NetFirewallRule -DisplayName "IT Toolkit Block {self.ip}" -Direction Outbound -Action Block -RemoteAddress {self.ip}'
            res = executor.run_powershell(cmd)
            self.write("Device has been isolated via local host firewall.")
        elif self.action == "shutdown":
            self.write("> Issuing WMI Remote Shutdown/Restart command...\n")
            res = executor.run_powershell(f"Restart-Computer -ComputerName {self.ip} -Force")
            if not res: res = "Shutdown command sent successfully (Requires appropriate AD/Remote credentials)."
            
        self.write(res + "\n\n> Task completed.")
        
    def write(self, text):
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")

class Node2D:
    def __init__(self, device, x, y):
        self.device = device
        self.x = x
        self.y = y
        self.base_radius = 22
        self.radius = 22
        self.target_radius = 22
        self.pulse = 0.0

class TopologyPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.nodes = {}
        self.edges = []
        self.running = True
        self.scan_in_progress = False
        self.hovered_node = None
        self.selected_node = None
        
        # Panning/Dragging state
        self._drag_data = {"item": None, "x": 0, "y": 0}
        self._pan_data = {"x": 0, "y": 0}
        self.zoom_scale = 1.0

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=12)
        toolbar.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(toolbar, text="🔍 Discover Network", font=FONTS["badge"], command=self.start_scan).pack(side="left", padx=10, pady=10)
        self.subnet_cbo = ctk.CTkComboBox(toolbar, values=["192.168.1.0/24", "10.0.0.0/24", "172.16.0.0/24", "127.0.0.1/32"], width=180)
        self.subnet_cbo.pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(toolbar, text="⟲ Reset View", fg_color=COLORS["bg_tertiary"], width=100, command=self.reset_view).pack(side="right", padx=10, pady=10)
        ctk.CTkButton(toolbar, text="📸 Export Map", fg_color=COLORS["bg_tertiary"], width=100, command=self.export_png).pack(side="right", padx=5, pady=10)

        # Canvas Wrapper
        canvas_frame = ctk.CTkFrame(self, fg_color=COLORS["border"], corner_radius=12)
        canvas_frame.pack(fill="both", expand=True, padx=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg=get_color("bg_primary"), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_hover)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Button-2>", self.on_right_click)
        
        # Bottom Details
        self.details_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=90, corner_radius=12)
        self.details_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        self.details_frame.pack_propagate(False)
        
        self.details_lbl = ctk.CTkLabel(self.details_frame, text="Select a network node on the map to view endpoint telemetry.", font=FONTS["body"])
        self.details_lbl.pack(pady=30)
        
        self.draw_placeholder()
        self.animation_loop()

    def draw_placeholder(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            400, 300, 
            text="📡 Enterprise 2D Topology Engine\n\nClick 'Discover Network' to actively footprint infrastructure.", 
            fill=get_color("text_secondary"), font=("Segoe UI", 14), justify="center", tags="placeholder"
        )

    def start_scan(self):
        if self.scan_in_progress: return
        self.scan_in_progress = True
        self.nodes = {}
        self.edges = []
        subnet = self.subnet_cbo.get()
        self.canvas.delete("all")
        self.canvas.create_text(
            400, 300, 
            text=f"Analyzing footprint for {subnet}...\nIntercepting ICMP and Port metrics in real-time.", 
            fill=get_color("accent_cyan"), font=("Segoe UI", 14, "bold"), justify="center", tags="status"
        )
        self.details_lbl.configure(text=f"Scanning {subnet}...", text_color=COLORS["accent_orange"])
        threading.Thread(target=self._run_scan, args=(subnet,), daemon=True).start()

    def _run_scan(self, subnet):
        scanner = NetworkScanner()
        devices = scanner.scan_subnet(subnet)
        self.after(0, lambda: self._build_2d_network(devices))

    def _build_2d_network(self, devices):
        self.scan_in_progress = False
        self.canvas.delete("all")
        self.zoom_scale = 1.0

        if not devices:
            self.details_lbl.configure(text="Scan complete. No active nodes found.", text_color=COLORS["accent_red"])
            return

        self.details_lbl.configure(text=f"Map rendered. Discovered {len(devices)} active node(s).", text_color=COLORS["text_primary"])

        G = nx.Graph()
        for d in devices:
            G.add_node(d.ip, device=d)
        
        if len(devices) > 1:
            gw = sorted(devices, key=lambda d: d.ip)[0].ip 
            for d in devices:
                if d.ip != gw:
                    G.add_edge(gw, d.ip)

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10: w, h = 800, 600
        
        pos = nx.spring_layout(G, scale=min(w, h)*0.35, center=(w/2, h/2), iterations=150)
        
        for d in devices:
            x, y = pos[d.ip]
            self.nodes[d.ip] = Node2D(d, x, y)
            
        self.edges = [(u, v) for u, v in G.edges()]
        
        self.render_static_elements()

    def render_static_elements(self):
        """Draws the nodes and edges, assigning them tags to be updated smoothly."""
        self.canvas.delete("all")
        
        # Draw curved edges
        for u_ip, v_ip in self.edges:
            u, v = self.nodes[u_ip], self.nodes[v_ip]
            tag = f"edge_{u_ip}_{v_ip}"
            # Use smooth=True for bezier spline look
            self.canvas.create_line(u.x, u.y, v.x, v.y, fill=get_color("border_active"), width=2, smooth=True, tags=("edge", tag))

        # Draw nodes
        for ip, n in self.nodes.items():
            tag = f"node_{ip}"
            
            # Pulse ring (grows and fades)
            pulse_col = get_color("accent_cyan") if n.device.status == "online" else get_color("accent_red")
            self.canvas.create_oval(n.x, n.y, n.x, n.y, outline=pulse_col, width=1, tags=("pulse", f"pulse_{ip}"))
            
            # Outer boundary
            border_col = get_color("status_online") if n.device.status == "online" else get_color("status_offline")
            self.canvas.create_oval(n.x - n.radius, n.y - n.radius, n.x + n.radius, n.y + n.radius, 
                                    fill=get_color("bg_secondary"), outline=border_col, width=2, tags=(tag, f"bg_{ip}"))
            
            # Icon
            icon = DEVICE_ICONS.get(n.device.device_type, "❓")
            self.canvas.create_text(n.x, n.y, text=icon, fill=get_color("text_primary"), font=("Segoe UI", 16), tags=(tag, f"icon_{ip}"))
            
            # Label background & text
            name = n.device.hostname[:15] if n.device.hostname != "Unknown" else n.device.device_type.capitalize()
            self.canvas.create_rectangle(n.x - 40, n.y + 26, n.x + 40, n.y + 44, fill=get_color("bg_tertiary"), outline="", tags=(tag, f"lblbg_{ip}"))
            self.canvas.create_text(n.x, n.y + 35, text=name, fill=get_color("text_primary"), font=("Segoe UI", 9, "bold"), tags=(tag, f"lbl_{ip}"))
            self.canvas.create_text(n.x, n.y + 48, text=f"{n.device.ip}", fill=get_color("text_secondary"), font=("Segoe UI", 8), tags=(tag, f"sublbl_{ip}"))

    def animation_loop(self):
        """Smooth 60fps interpolation for hover radius and pulsing without redrawing everything."""
        if not self.running: return

        if self.nodes and not self.scan_in_progress:
            for ip, n in self.nodes.items():
                # Smooth radius interpolation
                if n.radius != n.target_radius:
                    n.radius += (n.target_radius - n.radius) * 0.2
                    if abs(n.radius - n.target_radius) < 0.5: n.radius = n.target_radius
                    
                    # Update node background circle size
                    r = n.radius * self.zoom_scale
                    self.canvas.coords(f"bg_{ip}", n.x - r, n.y - r, n.x + r, n.y + r)
                    # Update Selection Highlight if active
                    if self.selected_node == ip:
                        self.canvas.itemconfig(f"bg_{ip}", outline=get_color("accent_purple"), width=3)
                    else:
                        border_col = get_color("status_online") if n.device.status == "online" else get_color("status_offline")
                        self.canvas.itemconfig(f"bg_{ip}", outline=border_col, width=2)
                
                # Pulse Animation
                n.pulse += 0.02
                if n.pulse > 1.0: n.pulse = 0.0
                
                # Max pulse radius depends on zoom
                p_rad = (n.base_radius + (n.pulse * 15)) * self.zoom_scale
                p_alpha = max(0, 255 - int(n.pulse * 255))
                # Tkinter doesn't do alpha outline directly well, but we can fake it by fading to bg_primary
                # We'll just animate the size of a thin ring for a sleek radar effect
                self.canvas.coords(f"pulse_{ip}", n.x - p_rad, n.y - p_rad, n.x + p_rad, n.y + p_rad)

        self.after(16, self.animation_loop)

    def update_edge_coords(self):
        for u_ip, v_ip in self.edges:
            u, v = self.nodes[u_ip], self.nodes[v_ip]
            self.canvas.coords(f"edge_{u_ip}_{v_ip}", u.x, u.y, v.x, v.y)

    def update_all_node_coords(self):
        for ip, n in self.nodes.items():
            r = n.radius * self.zoom_scale
            self.canvas.coords(f"bg_{ip}", n.x - r, n.y - r, n.x + r, n.y + r)
            self.canvas.coords(f"icon_{ip}", n.x, n.y)
            
            # Label
            self.canvas.coords(f"lblbg_{ip}", n.x - 40, n.y + (26 * self.zoom_scale), n.x + 40, n.y + (44 * self.zoom_scale))
            self.canvas.coords(f"lbl_{ip}", n.x, n.y + (35 * self.zoom_scale))
            self.canvas.coords(f"sublbl_{ip}", n.x, n.y + (48 * self.zoom_scale))
        
        self.update_edge_coords()

    # --- Mouse Events ---
    def get_node_at(self, x, y):
        # Reverse search for top-most
        for ip, n in reversed(self.nodes.items()):
            r = n.radius * self.zoom_scale
            if (n.x - r <= x <= n.x + r) and (n.y - r <= y <= n.y + r):
                return ip
        return None

    def on_hover(self, event):
        if not self.nodes: return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        hovered = self.get_node_at(x, y)
        
        if hovered != self.hovered_node:
            # Revert old
            if self.hovered_node and self.hovered_node in self.nodes:
                self.nodes[self.hovered_node].target_radius = self.nodes[self.hovered_node].base_radius
            # Grow new
            self.hovered_node = hovered
            if self.hovered_node:
                self.nodes[self.hovered_node].target_radius = self.nodes[self.hovered_node].base_radius * 1.3
                self.canvas.config(cursor="hand2")
            else:
                self.canvas.config(cursor="")

    def on_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        target = self.get_node_at(x, y)
        if target:
            # Select Node
            if self.selected_node and self.selected_node in self.nodes:
                # Reset old selection color logic implicitly handled in animation loop
                pass
            self.selected_node = target
            self.show_device_details(target)
            
            # Start Drag
            self._drag_data["item"] = target
            self._drag_data["x"] = x
            self._drag_data["y"] = y
        else:
            self.selected_node = None
            self._drag_data["item"] = None
            self._pan_data["x"] = event.x
            self._pan_data["y"] = event.y

    def on_drag(self, event):
        if self._drag_data["item"]:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            dx = x - self._drag_data["x"]
            dy = y - self._drag_data["y"]
            
            n = self.nodes[self._drag_data["item"]]
            n.x += dx
            n.y += dy
            
            self._drag_data["x"] = x
            self._drag_data["y"] = y
            self.update_all_node_coords()
        elif self._pan_data["x"] != 0:
            dx = event.x - self._pan_data["x"]
            dy = event.y - self._pan_data["y"]
            self.canvas.move("all", dx, dy)
            self._pan_data["x"] = event.x
            self._pan_data["y"] = event.y

    def on_release(self, event):
        self._drag_data["item"] = None

    def on_zoom(self, event):
        scale = 1.1 if event.delta > 0 else 0.9
        self.zoom_scale *= scale
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        self.canvas.scale("all", x, y, scale)
        
        # Scale coordinates of logical nodes
        for ip, n in self.nodes.items():
            n.x = x + (n.x - x) * scale
            n.y = y + (n.y - y) * scale

    def on_right_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        target_ip = self.get_node_at(x, y)
        if not target_ip: return
        
        # Select on right click too
        self.selected_node = target_ip
        self.show_device_details(target_ip)
        
        menu = tk.Menu(self, tearoff=0, bg=get_color("bg_secondary"), fg=get_color("text_primary"), font=("Segoe UI", 10), activebackground=get_color("accent_blue"))
        menu.add_command(label=f"📡 Ping {target_ip}", command=lambda: QuickDiag(self, "ICMP Ping", target_ip, "ping"))
        menu.add_command(label=f"🛣️ Trace Route", command=lambda: QuickDiag(self, "Trace Route", target_ip, "tracert"))
        menu.add_command(label=f"🔓 Quick Port Scan", command=lambda: QuickDiag(self, "Port Fingerprint", target_ip, "scan"))
        menu.add_separator()
        menu.add_command(label="🛡️ Isolate IP (Firewall Block)", foreground=COLORS["accent_red"], command=lambda: QuickDiag(self, "Network Isolation", target_ip, "block"))
        menu.add_command(label="🛑 Force Remote Restart", foreground=COLORS["accent_orange"], command=lambda: QuickDiag(self, "Remote Shutdown", target_ip, "shutdown"))
        menu.add_separator()
        menu.add_command(label="📋 Copy IP Address", command=lambda: self.master.clipboard_append(target_ip))
        
        menu.post(event.x_root, event.y_root)

    def reset_view(self):
        if not self.nodes: return
        self._build_2d_network(list(n.device for n in self.nodes.values()))

    def show_device_details(self, ip):
        if ip not in self.nodes: return
        d = self.nodes[ip].device
        ports_str = ", ".join(map(str, d.open_ports)) if d.open_ports else "None detected"
        info = (
            f"🎯  IP Address: {d.ip}    |    🏷️ Hostname: {d.hostname}    |    💻 Type: {d.device_type.upper()}    |    🟢 Status: {d.status.upper()}\n"
            f"⏱️ Latency: {d.response_time}ms    |    🔓 Exposed Ports: {ports_str}    |    🕒 Last Seen: {d.last_seen.strftime('%H:%M:%S')}"
        )
        self.details_lbl.configure(text=info, text_color=COLORS["accent_cyan"])

    def export_png(self):
        try:
            self.canvas.update()
            x = self.canvas.winfo_rootx()
            y = self.canvas.winfo_rooty()
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            
            export_path = os.path.join(os.getcwd(), "exports", "topology", "network_map.png")
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            ImageGrab.grab(bbox=(x, y, x+w, y+h)).save(export_path)
            self.details_lbl.configure(text=f"✅ Successfully exported topology map to: {export_path}", text_color=COLORS["accent_green"])
        except Exception as e:
            self.details_lbl.configure(text=f"❌ Failed to export map: {e}", text_color=COLORS["accent_red"])

    def destroy(self):
        self.running = False
        super().destroy()
