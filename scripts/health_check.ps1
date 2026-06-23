$report = @{
    Hostname    = $env:COMPUTERNAME
    OS          = (Get-WmiObject Win32_OperatingSystem).Caption
    CPU         = (Get-WmiObject Win32_Processor).LoadPercentage
    RAM_Free_GB = [math]::Round((Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory/1MB, 2)
    Disk_Free   = (Get-PSDrive C).Free
    Uptime_Days = ((Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime).Days
    Last_User   = (Get-WmiObject Win32_ComputerSystem).UserName
}
$report | ConvertTo-Json
