from core.executor import executor

class AdminCommands:
    @staticmethod
    def get_local_users():
        return executor.run_powershell("Get-LocalUser")

    @staticmethod
    def get_local_groups():
        return executor.run_powershell("Get-LocalGroup")
