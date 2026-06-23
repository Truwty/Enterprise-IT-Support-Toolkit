import customtkinter as ctk
from theme import COLORS, FONTS, get_color
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import collections
from core.monitor import SystemMonitor

class PerformancePanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        toolbar = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        toolbar.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(toolbar, text="PERFORMANCE MONITOR", font=FONTS["heading"]).pack(side="left", padx=10)
        
        # Interactive Control Buttons
        self.btn_pause = ctk.CTkButton(toolbar, text="⏸ Pause", width=80, fg_color=COLORS["bg_tertiary"], command=self.toggle_pause)
        self.btn_pause.pack(side="right", padx=10, pady=5)
        
        self.is_paused = False

        # Setup Figure using active theme colors via get_color()
        self.fig = Figure(figsize=(10, 6), facecolor=get_color("graph_bg"))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # 4 Quadrants
        self.ax_cpu = self.fig.add_subplot(2, 2, 1)
        self.ax_ram = self.fig.add_subplot(2, 2, 2)
        self.ax_disk = self.fig.add_subplot(2, 2, 3)
        self.ax_net = self.fig.add_subplot(2, 2, 4)

        # Add spacing to prevent overlapping titles/axes
        self.fig.subplots_adjust(hspace=0.4, wspace=0.2, bottom=0.1, top=0.9, left=0.08, right=0.95)

        # 60 Second Rolling Window Data Buffers
        self.cpu_data = collections.deque([0]*60, maxlen=60)
        self.ram_data = collections.deque([0]*60, maxlen=60)
        self.disk_r_data = collections.deque([0]*60, maxlen=60)
        self.disk_w_data = collections.deque([0]*60, maxlen=60)
        self.net_s_data = collections.deque([0]*60, maxlen=60)
        self.net_r_data = collections.deque([0]*60, maxlen=60)
        
        self.monitor = SystemMonitor()
        self.running = True
        
        self.update_graphs()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.configure(text="▶ Resume", fg_color=COLORS["accent_blue"])
        else:
            self.btn_pause.configure(text="⏸ Pause", fg_color=COLORS["bg_tertiary"])

    def style_axis(self, ax, title, color_name):
        ax.set_facecolor(get_color("graph_bg"))
        ax.tick_params(colors=get_color("text_secondary"), labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(get_color("border"))
        ax.set_title(title, color=get_color("text_primary"), pad=10, fontsize=10)
        ax.grid(True, color=get_color("graph_grid"), linestyle='--', alpha=0.6)

    def update_graphs(self):
        if not self.running: return

        if not self.is_paused:
            # Pull Telemetry Data
            cpu = self.monitor.get_cpu_usage()
            ram = self.monitor.get_ram_usage()["percent"]
            rates = self.monitor.get_rates()

            # Update Queues
            self.cpu_data.append(cpu)
            self.ram_data.append(ram)
            self.disk_r_data.append(rates["disk_read_mb"])
            self.disk_w_data.append(rates["disk_write_mb"])
            self.net_s_data.append(rates["net_sent_mb"])
            self.net_r_data.append(rates["net_recv_mb"])
            
            x_range = range(60)

            # --- Plot CPU ---
            self.ax_cpu.clear()
            self.style_axis(self.ax_cpu, "CPU Utilization (%)", "graph_cpu")
            self.ax_cpu.plot(x_range, self.cpu_data, color=get_color("graph_cpu"), linewidth=1.5)
            self.ax_cpu.fill_between(x_range, self.cpu_data, color=get_color("graph_cpu"), alpha=0.15)
            self.ax_cpu.set_ylim(0, 100)

            # --- Plot RAM ---
            self.ax_ram.clear()
            self.style_axis(self.ax_ram, "Memory Usage (%)", "graph_ram")
            self.ax_ram.plot(x_range, self.ram_data, color=get_color("graph_ram"), linewidth=1.5)
            self.ax_ram.fill_between(x_range, self.ram_data, color=get_color("graph_ram"), alpha=0.15)
            self.ax_ram.set_ylim(0, 100)

            # --- Plot Disk I/O ---
            self.ax_disk.clear()
            self.style_axis(self.ax_disk, "Disk I/O Throughput (MB/s)", "graph_disk")
            self.ax_disk.plot(x_range, self.disk_r_data, color=get_color("accent_green"), label="Read", linewidth=1.5)
            self.ax_disk.plot(x_range, self.disk_w_data, color=get_color("accent_orange"), label="Write", linewidth=1.5)
            self.ax_disk.legend(loc="upper left", fontsize=8, facecolor=get_color("bg_secondary"), edgecolor="none", labelcolor=get_color("text_primary"))
            max_io = max(max(self.disk_r_data), max(self.disk_w_data), 1.0)
            self.ax_disk.set_ylim(0, max_io * 1.2)

            # --- Plot Network ---
            self.ax_net.clear()
            self.style_axis(self.ax_net, "Network Throughput (MB/s)", "graph_network")
            self.ax_net.plot(x_range, self.net_r_data, color=get_color("accent_blue"), label="Recv", linewidth=1.5)
            self.ax_net.plot(x_range, self.net_s_data, color=get_color("accent_cyan"), label="Sent", linewidth=1.5)
            self.ax_net.legend(loc="upper left", fontsize=8, facecolor=get_color("bg_secondary"), edgecolor="none", labelcolor=get_color("text_primary"))
            max_net = max(max(self.net_r_data), max(self.net_s_data), 1.0)
            self.ax_net.set_ylim(0, max_net * 1.2)
            
            self.canvas.draw()
        
        # Schedule next render loop
        self.after(1000, self.update_graphs)

    def destroy(self):
        self.running = False
        try:
            self.fig.clear()
            import matplotlib.pyplot as plt
            plt.close(self.fig)
        except Exception:
            pass
        super().destroy()
