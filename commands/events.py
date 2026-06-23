from core.executor import executor

class EventCommands:
    @staticmethod
    def get_system_errors():
        return executor.run_powershell("Get-EventLog -LogName System -EntryType Error -Newest 50")

    @staticmethod
    def get_application_errors():
        return executor.run_powershell("Get-EventLog -LogName Application -EntryType Error -Newest 50")
