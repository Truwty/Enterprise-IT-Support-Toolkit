import subprocess

class Executor:
    """PowerShell/SSH executor engine."""
    
    def run_powershell(self, command: str) -> str:
        try:
            # Added encoding='utf-8' and errors='replace' to fix UnicodeDecodeError on Windows
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            # If powershell writes to stderr, append it so we don't lose error context
            out = result.stdout.strip()
            if result.stderr:
                out += f"\n[Error/Warning]: {result.stderr.strip()}"
            return out
        except Exception as e:
            return f"Execution Failed: {str(e)}"

    def run_command(self, cmd: list) -> str:
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Execution Failed: {str(e)}"
            
executor = Executor()
