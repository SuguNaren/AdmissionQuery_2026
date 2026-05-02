function Get-UsablePython {
    $commandCandidates = @("py", "python", "python3")
    foreach ($name in $commandCandidates) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if (-not $command) {
            continue
        }

        if ($command.Source -like "*WindowsApps\\python*.exe") {
            continue
        }

        return $command.Source
    }

    $pathCandidates = @(
        "$env:PYTHON_BIN",
        "$env:LOCALAPPDATA\\Programs\\Python\\Python313\\python.exe",
        "$env:LOCALAPPDATA\\Programs\\Python\\Python312\\python.exe",
        "$env:LOCALAPPDATA\\Programs\\Python\\Python311\\python.exe",
        "$env:LOCALAPPDATA\\Programs\\Python\\Python310\\python.exe",
        "C:\\Python313\\python.exe",
        "C:\\Python312\\python.exe",
        "C:\\Python311\\python.exe",
        "C:\\Python310\\python.exe",
        "C:\\Program Files\\IBM\\SPSS Statistics\\Python3\\python.exe"
    )

    foreach ($path in $pathCandidates) {
        if ($path -and (Test-Path $path)) {
            return $path
        }
    }

    return $null
}

$root = $PSScriptRoot
$pythonExe = Get-UsablePython

if (-not $pythonExe) {
    Write-Host "Python was not found on this machine."
    exit 1
}

$stdoutLog = Join-Path $root "chatbot-server.out.log"
$stderrLog = Join-Path $root "chatbot-server.err.log"
$runScript = Join-Path $root "run.py"

Start-Process `
    -FilePath $pythonExe `
    -ArgumentList @($runScript, "--serve") `
    -WorkingDirectory $root `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -WindowStyle Hidden `
    -PassThru | Select-Object Id, ProcessName
