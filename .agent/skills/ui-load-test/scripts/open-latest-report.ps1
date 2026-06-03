# open-latest-report.ps1 - Open the most recent HTML report for a flow.
#
# Usage:
#   .\scripts\open-latest-report.ps1                  # defaults to flow=search
#   .\scripts\open-latest-report.ps1 -Flow search
#   .\scripts\open-latest-report.ps1 -Flow checkout

param(
    [string]$Flow = "search",
    [string]$ProjectRoot = "C:\Users\costrategix\PycharmProjects\PECO-Load-Tester"
)

$ErrorActionPreference = "Stop"

$reportsDir = Join-Path $ProjectRoot "reports\$Flow"

if (-not (Test-Path $reportsDir)) {
    Write-Host "No reports directory found for flow '$Flow'" -ForegroundColor Red
    Write-Host "  Expected: $reportsDir" -ForegroundColor Yellow
    exit 1
}

$latest = Get-ChildItem -Path $reportsDir -Filter "*_report.html" |
          Sort-Object LastWriteTime -Descending |
          Select-Object -First 1

if (-not $latest) {
    Write-Host "No HTML reports found in $reportsDir" -ForegroundColor Red
    exit 1
}

Write-Host "Opening: $($latest.FullName)" -ForegroundColor Green
Write-Host "  Generated: $($latest.LastWriteTime)" -ForegroundColor DarkGray
Invoke-Item $latest.FullName
