import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"
SCRIPTS_DIR = BASE_DIR / "scripts"
ASSETS_DIR = BASE_DIR / "assets"

# App Info
APP_NAME = "Enterprise IT Toolkit"
APP_VERSION = "3.0"

# Defaults
DEFAULT_SUBNET = "192.168.1.0/24"
SCAN_TIMEOUT_MS = 500
MAX_THREADS = 50
GRAPH_REFRESH_SEC = 1

# Database
DB_PATH = DATA_DIR / "toolkit.db"
