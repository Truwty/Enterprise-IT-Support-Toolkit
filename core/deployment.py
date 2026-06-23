from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading
import time

@dataclass
class Machine:
    hostname: str
    ip: str
    username: str
    password: str

@dataclass
class DeployResult:
    machine: Machine
    success: bool
    output: str
    duration: float

class DeploymentEngine:
    """Fully functional Parallel remote deployment engine using WinRM and Paramiko."""
    def __init__(self):
        self.target_machines: list[Machine] = []
        self.max_concurrent: int = 5

    def add_machine(self, machine: Machine) -> None:
        self.target_machines.append(machine)

    def deploy_script(self, machines: list[Machine], script: str, callback=None) -> None:
        def _runner():
            with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
                futures = {executor.submit(self.execute_on_machine, m, script): m for m in machines}
                for f in futures:
                    res = f.result()
                    if callback: callback(res)
        threading.Thread(target=_runner, daemon=True).start()

    def execute_on_machine(self, machine: Machine, script: str) -> DeployResult:
        start = time.time()
        
        # 1. WinRM Attempt (Windows)
        try:
            import winrm
            session = winrm.Session(machine.ip, auth=(machine.username, machine.password), transport='ntlm')
            r = session.run_ps(script)
            duration = time.time() - start
            success = r.status_code == 0
            return DeployResult(machine, success, r.std_out.decode() if success else r.std_err.decode(), duration)
        except Exception as e_winrm:
            # 2. Paramiko SSH Fallback (Linux / OpenSSH Windows)
            try:
                import paramiko
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(machine.ip, username=machine.username, password=machine.password, timeout=5)
                stdin, stdout, stderr = client.exec_command(script)
                out = stdout.read().decode()
                err = stderr.read().decode()
                client.close()
                duration = time.time() - start
                success = True if not err else False
                return DeployResult(machine, success, out if not err else err, duration)
            except Exception as e_ssh:
                duration = time.time() - start
                error_msg = f"Failed to connect.\nWinRM: {str(e_winrm)}\nSSH: {str(e_ssh)}"
                return DeployResult(machine, False, error_msg, duration)
