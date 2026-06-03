# switch-pool.ps1 - Switch the active queries.json to a named pool.
#
# Usage:
#   .\scripts\switch-pool.ps1 -Pool smoke
#   .\scripts\switch-pool.ps1 -Pool full
#   .\scripts\switch-pool.ps1 -Pool full-geocoded
#   .\scripts\switch-pool.ps1 -Pool edge-cases
#   .\scripts\switch-pool.ps1 -Pool <custom-name>    # uses queries-<custom-name>.json

param(
    [Parameter(Mandatory=$true)]
    [string]$Pool,

    [string]$ProjectRoot = "C:\Users\costrategix\PycharmProjects\PECO-Load-Tester"
)

$ErrorActionPreference = "Stop"

$source = Join-Path $ProjectRoot "queries-$Pool.json"
$target = Join-Path $ProjectRoot "queries.json"

if (-not (Test-Path $source)) {
    Write-Host "Pool file not found: $source" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available pools in $ProjectRoot :" -ForegroundColor Yellow
    Get-ChildItem -Path $ProjectRoot -Filter "queries-*.json" | ForEach-Object {
        $name = $_.BaseName -replace "^queries-", ""
        Write-Host "  - $name"
    }
    exit 1
}

Copy-Item -Path $source -Destination $target -Force
$count = (Get-Content $target -Raw | ConvertFrom-Json).Count
Write-Host "Switched to pool '$Pool' ($count queries)" -ForegroundColor Green
Write-Host "  Active: $target" -ForegroundColor DarkGray
