from core.executor import executor

class DiskCommands:
    @staticmethod
    def get_logical_disks():
        return executor.run_powershell("Get-WmiObject Win32_LogicalDisk")

    @staticmethod
    def get_physical_disks():
        return executor.run_powershell("Get-PhysicalDisk")
