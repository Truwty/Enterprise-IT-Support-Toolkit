# scripts/cleanup.ps1
Write-Host "Running remote disk cleanup..."
Clear-RecycleBin -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Cleanup complete."
