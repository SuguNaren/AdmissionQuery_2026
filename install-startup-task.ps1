$taskName = "SMC Chatbot Server"
$root = $PSScriptRoot
$scriptPath = Join-Path $root "start-background.ps1"

if (-not (Test-Path $scriptPath)) {
    Write-Host "Missing start-background.ps1 at $scriptPath"
    exit 1
}

$powershellExe = Join-Path $env:WINDIR "System32\WindowsPowerShell\v1.0\powershell.exe"
$action = New-ScheduledTaskAction -Execute $powershellExe -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Force

Write-Host "Scheduled task '$taskName' created."
Write-Host "It will launch the chatbot server at Windows startup, even without VS Code or a logged-in user session."
