from core.executor import executor

class NetworkCommands:
    @staticmethod
    def get_ipconfig():
        return executor.run_powershell("ipconfig /all")

    @staticmethod
    def ping(host: str):
        return executor.run_powershell(f"ping {host}")

    @staticmethod
    def tracert(host: str):
        return executor.run_powershell(f"tracert {host}")

    @staticmethod
    def get_netstat():
        return executor.run_powershell("netstat -ano")
