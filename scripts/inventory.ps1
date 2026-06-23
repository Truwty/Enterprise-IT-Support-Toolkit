# scripts/inventory.ps1
Get-WmiObject -Class Win32_Product | Select-Object Name, Version | ConvertTo-Json
