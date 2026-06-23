"""
Enterprise IT Support Toolkit v3.0
Entry point with automatic admin elevation.
"""

import sys
import ctypes
import subprocess
from pathlib import Path

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def elevate() -> None:
    """Relaunch with admin rights."""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas",
        sys.executable,
        " ".join(sys.argv),
        None, 1
    )
    sys.exit(0)

def setup_environment() -> None:
    """Create required directories."""
    for directory in ["logs", "data", "exports/reports",
                     "exports/graphs", "exports/topology"]:
        Path(directory).mkdir(parents=True, exist_ok=True)

def main() -> None:
    setup_environment()

    if not is_admin():
        # Ask user if they want to elevate
        try:
            result = ctypes.windll.user32.MessageBoxW(
                None,
                "Some features require administrator privileges.\n\n"
                "Would you like to restart as Administrator?\n\n"
                "Click 'No' to continue with limited features.",
                "Enterprise IT Toolkit — Admin Required",
                0x04 | 0x30  # Yes/No | Warning icon
            )
            if result == 6:  # Yes
                elevate()
        except AttributeError:
            # Non-windows platform, ignore
            pass

    from app import ITToolkitApp
    app = ITToolkitApp()
    app.mainloop()

if __name__ == "__main__":
    main()
