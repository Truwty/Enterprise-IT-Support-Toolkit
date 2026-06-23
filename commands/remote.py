from core.executor import executor

class RemoteCommands:
    @staticmethod
    def test_winrm(host: str):
        return executor.run_powershell(f"Test-WSMan -ComputerName {host}")
