# Build dist\SafeCodeSessionGuard\SafeCodeSessionGuard.exe and a .zip for distribution.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

function Invoke-Checked {
    & $args[0] $args[1..($args.Count - 1)]
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $args" }
}

$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
if (-not (Test-Path .venv)) { Invoke-Checked $python -m venv .venv }
Invoke-Checked .venv\Scripts\python.exe -m pip install -q -r requirements-dev.txt
Invoke-Checked .venv\Scripts\pyinstaller.exe --noconfirm --clean SafeCodeSessionGuard.spec

$version = (& .venv\Scripts\python.exe -c "import sessionguard; print(sessionguard.__version__)").Trim()
$zip = "dist\SafeCodeSessionGuard-$version-windows-x64.zip"
Compress-Archive -Path dist\SafeCodeSessionGuard -DestinationPath $zip -Force
Write-Host "Built: dist\SafeCodeSessionGuard\SafeCodeSessionGuard.exe, $zip"
