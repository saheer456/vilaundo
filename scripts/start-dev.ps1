# Start both backend and frontend for local development (PowerShell)
# Usage: .\scripts\start-dev.ps1

param(
  [switch]$NoInstall
)

Set-StrictMode -Version Latest

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location (Join-Path $root "..")

Write-Host "Starting VilaUndo development environment in: $(Get-Location)"

# Disable scheduler during local dev and point frontend to local backend
$env:DISABLE_SCHEDULER = '1'
$env:VITE_API_URL = 'http://127.0.0.1:8000'

if (-not $NoInstall) {
  Write-Host "Installing frontend dependencies (npm ci)"
  Push-Location -Path "frontend"
  npm ci
  Pop-Location
}

Write-Host "Starting backend: python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
$python = "python"
$backendArgs = @("-m", "uvicorn", "backend.app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000")
$backendProc = Start-Process -FilePath $python -ArgumentList $backendArgs -WorkingDirectory (Get-Location) -PassThru

Write-Host "Starting frontend: npm run dev (in ./frontend)"
$frontendProc = Start-Process -FilePath "npm" -ArgumentList @("run", "dev") -WorkingDirectory (Join-Path (Get-Location) "frontend") -PassThru

Write-Host "Backend started (PID: $($backendProc.Id)). Frontend started (PID: $($frontendProc.Id))."
Write-Host "To stop processes: Stop-Process -Id <PID>"
