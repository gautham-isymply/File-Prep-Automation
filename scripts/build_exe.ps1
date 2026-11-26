$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    uv sync --extra build --extra dev
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
    uv run --no-sync python -m PyInstaller --noconfirm factoryprep.spec
    if ($LASTEXITCODE -ne 0) { throw 'Executable build failed' }
    uv run --no-sync python scripts/smoke_exe.py dist/factoryprep.exe
    if ($LASTEXITCODE -ne 0) { throw 'Standalone executable smoke check failed' }
    Write-Host 'Built dist\factoryprep.exe'
} finally {
    Pop-Location
}
