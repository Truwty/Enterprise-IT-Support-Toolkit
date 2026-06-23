# ⚡ Enterprise IT Support Toolkit v3.0

> **🤖 Hybrid AI Development (Vibe Coded)**
> This enterprise-grade application was built using a hybrid development approach, leveraging advanced AI Agents to rapidly prototype and "vibe code" highly complex backend systems alongside human architectural oversight. 
> 
> **Specifically, the AI independently architected and generated:**
> - The custom **zero-latency multi-threaded network traversal algorithm** that maps massive enterprise subnets in milliseconds.
> - The mathematical cubic-bezier easing functions required to render the 60fps **interactive NetworkX Topology Map**.
> - The complex parallel threading logic bridging **Microsoft Graph API and WinRM integrations** for the Remote Deployment engine.
> - The self-healing **SQLite3 Database concurrency architecture** that handles high-frequency read/writes from the live Matplotlib telemetry loops.
> - The autonomous **Packet Sniffer logic** and automated **Cloud Webhook generation** pipelines.

## 🌟 Overview
The most comprehensive, professional, production-ready Windows IT Support Toolkit built with Python. Designed to give System Administrators and IT Support Technicians a single pane of glass for network discovery, hardware telemetry, remote deployment, and automated alerting.

## 🚀 Core Features
- **Dashboard**: High-level system overview with real-time SQLite KPI tracking and Host OS telemetry (CPU, RAM, Disk).
- **Topology Map**: Visual network mapping using NetworkX layouts, interactive node dragging, and active IP/Port footprinting. Right-click nodes to isolate IPs via Firewall or force remote WMI restarts.
- **Performance Graphs**: Live real-time Matplotlib graphs tracking CPU, RAM, Disk I/O, and Network Throughput with dynamic Y-axis scaling and pause/resume functionality.
- **Active Directory & Azure/Intune**: Native AD querying tools via LDAP/RSAT, plus Microsoft Graph API integration for fetching Entra ID and Intune devices.
- **Remote Deployment**: Multi-machine parallel script execution engine targeting endpoints via WinRM and Paramiko SSH. Includes local execution log exporting.
- **Compliance & Reporting**: Generate physical PDF and CSV snapshot documents of your network footprints using `fpdf2`.
- **Cloud Helpdesk Webhooks**: Automatically sync your locally generated tickets directly to ServiceNow, Jira, or Zendesk via REST API webhooks.
- **Automated Remediation**: One-click remediation engine to fix common Windows faults (Flush DNS, Restart Print Spoolers, SFC Scans).
- **Alert Engine**: Fully functional background daemon that monitors hardware thresholds, sounds desktop alarms, and dispatches payload summaries via SMTP/TLS.

---

## 🛠️ Full Technology Stack
- **Python 3.11+**
- **GUI**: CustomTkinter 5.2+
- **Data Visualization**: Matplotlib 3.7+, NetworkX 3.1+
- **Networking & Security**: Scapy, Requests, MSAL (Microsoft Authentication Library)
- **Remote Execution**: Paramiko (SSH), PyWinRM (Windows Remote Management)
- **Storage & Telemetry**: SQLite3, Psutil
- **Reporting**: FPDF2

---

## 📖 Installation & Setup Tutorial

Follow this step-by-step roadmap to get the toolkit running on your local machine or compiled into a distributable `.exe`.

### Step 1: Prerequisites
- Install **Python 3.11** or higher.
- *(Optional but recommended for packet sniffing)* Install [Npcap](https://npcap.com/) (Windows) or `libpcap` (Linux) to allow Scapy to capture network packets natively.

### Step 2: Clone the Repository
Open your terminal or command prompt and clone the project:
```bash
git clone https://github.com/yourusername/EnterpriseITToolkit.git
cd EnterpriseITToolkit
```

### Step 3: Create a Virtual Environment (Recommended)
Isolate your dependencies so they don't conflict with other Python projects:
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 4: Install Dependencies
Install all the required packages explicitly requested by the toolkit:
```bash
pip install -r requirements.txt
```

### Step 5: Launch the Application
Run the entry point script. The application includes a Windows hook that will automatically prompt you for **Administrator privileges** via UAC. This is required for deep WMI queries, firewall manipulation, and packet sniffing.
```bash
python main.py
```

---

## 📦 Compiling to a Standalone Executable (.exe)

If you want to distribute this tool to other IT Technicians without them needing to install Python or use the command line, you can compile it into a single portable application.

1. Ensure PyInstaller is installed in your environment:
   ```bash
   pip install pyinstaller
   ```
2. Run the provided PyInstaller specification file. This file automatically bundles all CustomTkinter assets, Matplotlib backends, and local scripts:
   ```bash
   pyinstaller build.spec --clean
   ```
3. Once the build finishes (it may take a few minutes), navigate to the newly created `dist/` folder.
4. You will find `EnterpriseITToolkit.exe` (or the equivalent Linux/macOS binary). You can now move this file anywhere and run it natively!

---

## 🌐 Network & Security Requirements
To utilize the remote features of this toolkit across your enterprise network, ensure the following ports and services are permitted through your firewalls:
- **WinRM (Port 5985):** Must be enabled on target Windows machines for remote powershell deployments. Run `Enable-PSRemoting -Force` on endpoints.
- **SSH (Port 22):** Must be enabled for Linux targets or OpenSSH-enabled Windows hosts.
- **ICMP Echo Request:** Must be allowed through target firewalls for the Topology ping sweeper to map endpoints correctly.
- **Database Security:** SMTP App Passwords and Azure AD Client Secrets are saved in the local SQLite database (`data/toolkit.db`). Ensure disk-level encryption (e.g., BitLocker) is active on the host machine running the toolkit.

---

## 📁 Project File Structure
```text
EnterpriseITToolkit/
├── main.py                 # Entry point with admin elevation hooks
├── app.py                  # Root application window and panel routing
├── config.py               # Constants and configuration paths
├── theme.py                # Colors, fonts, and light/dark theme switcher
├── logger.py               # Application logging setup
├── database.py             # SQLite database schemas and thread-safe operations
├── requirements.txt        # Python package dependencies
├── build.spec              # PyInstaller build specification
│
├── commands/               # PowerShell/CMD execution wrappers
│   ├── network.py          # Ping, tracert, ipconfig, netstat
│   ├── system.py           # Process and service management
│   ├── disk.py             # Logical and physical disk queries
│   ├── events.py           # Windows Event Log parsers
│   ├── admin.py            # Local user/group management
│   └── remote.py           # WinRM test connections
│
├── core/                   # Core backend engines and logic
│   ├── executor.py         # Subprocess threading engine (UTF-8 safe)
│   ├── scanner.py          # Threaded IP/Port network footprinting
│   ├── sniffer.py          # Scapy packet interception engine
│   ├── monitor.py          # Real-time hardware telemetry calculations
│   ├── alerting.py         # SMTP alert daemon and local system hooks
│   ├── deployment.py       # WinRM/SSH parallel script executor
│   ├── reporting.py        # PDF/CSV compliance engine
│   ├── webhooks.py         # Cloud Helpdesk API sync engine
│   └── scheduler.py        # Background task queue
│
├── ui/                     # User interface components
│   ├── header.py           # Top navigation and user profile
│   ├── sidebar.py          # Main menu routing
│   ├── statusbar.py        # Bottom status and execution timers
│   ├── console.py          # Terminal output widget with persistent logging
│   ├── dialogs.py          # Modal popups
│   │
│   └── panels/             # Individual application tabs/screens
│       ├── dashboard.py    # Main KPI and telemetry view
│       ├── topology.py     # NetworkX 2D interactive canvas renderer
│       ├── performance.py  # Matplotlib quad-graph layout
│       ├── remote_deploy.py# Deployment entry forms
│       ├── alerts.py       # SMTP and rule configuration
│       ├── tickets.py      # SQLite Helpdesk interface
│       ├── ad_tools.py     # Active Directory querying tools
│       ├── azure_tools.py  # Azure AD and Intune MSAL Graph API integrations
│       ├── remediation.py  # Automated fault fixing suite
│       ├── packet_sniffer.py
│       ├── reporting.py    
│       ├── settings.py     # App configuration tabview
│       └── ...             
│
├── scripts/                # Remote execution payloads
│   ├── agent.py            # Cross-platform persistent telemetry daemon
│   ├── health_check.ps1    
│   ├── deploy_agent.ps1
│   ├── cleanup.ps1
│   └── inventory.ps1
│
├── assets/                 # Icons and visual assets
├── data/                   # SQLite DB storage (auto-generated)
├── logs/                   # Log files (auto-generated)
└── exports/                # Exported reports and graphs (auto-generated)
```#   E n t e r p r i s e - I T - S u p p o r t - T o o l k i t  
 