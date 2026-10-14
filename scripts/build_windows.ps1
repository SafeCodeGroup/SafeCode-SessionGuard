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
# PyInstaller builds for the CPU of the Python it runs on (x64, 32-bit x86 or ARM64).
$plat = (& .venv\Scripts\python.exe -c "import sysconfig; print(sysconfig.get_platform())").Trim()
$arch = @{ "win-amd64" = "x64"; "win32" = "x86"; "win-arm64" = "arm64" }[$plat]
if (-not $arch) { throw "Unknown Python platform $plat" }
$zip = "dist\SafeCodeSessionGuard-$version-windows-$arch.zip"
Compress-Archive -Path dist\SafeCodeSessionGuard -DestinationPath $zip -Force
Write-Host "Built: dist\SafeCodeSessionGuard\SafeCodeSessionGuard.exe, $zip"
