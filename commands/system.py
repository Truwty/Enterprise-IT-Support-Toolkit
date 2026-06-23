from core.executor import executor

class SystemCommands:
    @staticmethod
    def get_system_info():
        return executor.run_powershell("systeminfo")

    @staticmethod
    def get_processes():
        return executor.run_powershell("Get-Process | Sort-Object CPU -Descending | Select-Object -First 20")

    @staticmethod
    def kill_process(pid: str):
        return executor.run_powershell(f"Stop-Process -Id {pid} -Force")

    @staticmethod
    def get_services():
        return executor.run_powershell("Get-Service")
