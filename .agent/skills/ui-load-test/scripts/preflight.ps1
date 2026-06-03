# preflight.ps1 - Verify environment is ready for PECO load testing.
#
# Usage:
#   .\scripts\preflight.ps1
#
# Exit codes:
#   0 = all checks passed
#   1 = one or more checks failed

$ErrorActionPreference = "Continue"
$failed = $false

Write-Host ""
Write-Host "PECO Load Tester - Preflight Check" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

function Test-Command {
    param([string]$Name, [string]$Command, [string]$MinVersion, [string]$InstallUrl)
    Write-Host -NoNewline "  $Name ... "
    try {
        $output = & cmd /c "$Command 2>&1"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK" -ForegroundColor Green
            Write-Host "    $($output | Select-Object -First 1)" -ForegroundColor DarkGray
            return $true
        } else {
            Write-Host "MISSING" -ForegroundColor Red
            Write-Host "    Install: $InstallUrl" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "MISSING" -ForegroundColor Red
        Write-Host "    Install: $InstallUrl" -ForegroundColor Yellow
        return $false
    }
}

if (-not (Test-Command -Name "Node.js (>=18)" -Command "node --version" -InstallUrl "https://nodejs.org/")) { $failed = $true }
if (-not (Test-Command -Name "k6" -Command "k6 version" -InstallUrl "https://k6.io/docs/get-started/installation/")) { $failed = $true }

Write-Host ""
Write-Host "Project directory check" -ForegroundColor Cyan
$projectPath = "C:\Users\costrategix\PycharmProjects\PECO-Load-Tester"
Write-Host -NoNewline "  $projectPath ... "
if (Test-Path $projectPath) {
    Write-Host "OK" -ForegroundColor Green
    $compiler = Join-Path $projectPath "peco_smart_compiler_v1.js"
    Write-Host -NoNewline "  peco_smart_compiler_v1.js ... "
    if (Test-Path $compiler) {
        Write-Host "OK" -ForegroundColor Green
    } else {
        Write-Host "MISSING" -ForegroundColor Red
        $failed = $true
    }
} else {
    Write-Host "MISSING" -ForegroundColor Red
    Write-Host "    Expected at: $projectPath" -ForegroundColor Yellow
    $failed = $true
}

Write-Host ""
if ($failed) {
    Write-Host "Preflight FAILED. Fix the above before proceeding." -ForegroundColor Red
    exit 1
} else {
    Write-Host "Preflight PASSED. Ready to run load tests." -ForegroundColor Green
    exit 0
}
