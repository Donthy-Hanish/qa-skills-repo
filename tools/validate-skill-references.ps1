<#
.SYNOPSIS
    Validate that every file referenced in SKILL.md actually exists on disk.

.DESCRIPTION
    Scans each skill's SKILL.md for references to files in references/, scripts/,
    and evals/ directories. Reports missing files, orphaned files (exist on disk
    but not mentioned in SKILL.md), and provides a pass/fail summary.

.USAGE
    cd C:\Users\costrategix\PycharmProjects\qa-skills-repo\.agent\skills
    .\validate-skill-references.ps1
    .\validate-skill-references.ps1 -SkillName appium-mobile-tester
    .\validate-skill-references.ps1 -OutputReport .\validation-report.txt
#>

param(
    [string]$SkillName = "",
    [string]$OutputReport = ""
)

$ErrorActionPreference = "Continue"

function Write-Status($icon, $msg) {
    Write-Host "  $icon $msg"
}

function Validate-Skill($skillDir) {
    $name = Split-Path $skillDir -Leaf
    $skillMd = Join-Path $skillDir "SKILL.md"

    if (-not (Test-Path $skillMd)) {
        Write-Host "`n--- $name ---" -ForegroundColor Yellow
        Write-Status "!!" "SKILL.md not found - skipping"
        return @{ Name = $name; Status = "SKIP"; Missing = @(); Orphaned = @(); Referenced = @() }
    }

    Write-Host "`n--- $name ---" -ForegroundColor Cyan
    $content = Get-Content $skillMd -Raw

    # Extract all file references matching references/, scripts/, evals/ patterns
    $referencedFiles = @()

    # Match patterns like: references/filename.ext, scripts/filename.ext, evals/filename.ext
    $matches = [regex]::Matches($content, '(?:references|scripts|evals)/[\w\-\.]+(?:\.[\w]+)')
    foreach ($m in $matches) {
        $referencedFiles += $m.Value
    }

    # Deduplicate
    $referencedFiles = $referencedFiles | Sort-Object -Unique

    Write-Status "i" "Referenced files in SKILL.md: $($referencedFiles.Count)"

    # Check each referenced file exists
    $missing = @()
    $found = @()
    foreach ($ref in $referencedFiles) {
        $fullPath = Join-Path $skillDir $ref
        if (Test-Path $fullPath) {
            Write-Status ([char]0x2713) "$ref" 
            $found += $ref
        } else {
            Write-Status "X" "$ref - MISSING" 
            $missing += $ref
        }
    }

    # Check for orphaned files (exist on disk but not in SKILL.md)
    $orphaned = @()
    foreach ($subdir in @("references", "scripts", "evals")) {
        $subdirPath = Join-Path $skillDir $subdir
        if (Test-Path $subdirPath) {
            $diskFiles = Get-ChildItem $subdirPath -File -Recurse | ForEach-Object {
                $_.FullName.Replace("$skillDir\", "").Replace("\", "/")
            }
            foreach ($diskFile in $diskFiles) {
                if ($diskFile -notin $referencedFiles) {
                    # Check if the filename (without path) is mentioned anywhere
                    $fileName = Split-Path $diskFile -Leaf
                    if ($content -match [regex]::Escape($fileName)) {
                        # Referenced by filename only, not full path - warn
                        Write-Status "~" "$diskFile - on disk, referenced by filename only"
                    } else {
                        Write-Status "?" "$diskFile - on disk but NOT referenced in SKILL.md"
                        $orphaned += $diskFile
                    }
                }
            }
        }
    }

    # Check required files exist
    $requiredFiles = @("SKILL.md", "requirements.json")
    $requiredDirs = @("evals")
    $requiredEvals = @("evals/trigger-eval.json", "evals/test-prompts.json")

    Write-Host ""
    Write-Status "i" "Required files check:"
    foreach ($req in $requiredFiles) {
        $reqPath = Join-Path $skillDir $req
        if (Test-Path $reqPath) {
            Write-Status ([char]0x2713) "$req"
        } else {
            Write-Status "X" "$req - MISSING (required)"
            $missing += $req
        }
    }
    foreach ($req in $requiredEvals) {
        $reqPath = Join-Path $skillDir $req
        if (Test-Path $reqPath) {
            Write-Status ([char]0x2713) "$req"
        } else {
            Write-Status "X" "$req - MISSING (required)"
            $missing += $req
        }
    }

    # Summary for this skill
    Write-Host ""
    if ($missing.Count -eq 0 -and $orphaned.Count -eq 0) {
        Write-Status ([char]0x2713) "PASS - All references valid, no orphaned files" 
    } elseif ($missing.Count -gt 0) {
        Write-Status "X" "FAIL - $($missing.Count) missing file(s)" 
    }
    if ($orphaned.Count -gt 0) {
        Write-Status "~" "WARN - $($orphaned.Count) orphaned file(s) (on disk but not in SKILL.md)"
    }

    return @{
        Name = $name
        Status = if ($missing.Count -eq 0) { "PASS" } else { "FAIL" }
        Missing = $missing
        Orphaned = $orphaned
        Referenced = $referencedFiles
        Found = $found
    }
}

# Main
Write-Host "============================================" -ForegroundColor White
Write-Host "  Skill Reference Integrity Validator" -ForegroundColor White
Write-Host "============================================" -ForegroundColor White

$basePath = Get-Location
$results = @()

if ($SkillName) {
    $skillDir = Join-Path $basePath $SkillName
    if (Test-Path $skillDir) {
        $results += Validate-Skill $skillDir
    } else {
        Write-Host "Skill not found: $SkillName" -ForegroundColor Red
        exit 1
    }
} else {
    $skillDirs = Get-ChildItem $basePath -Directory | Where-Object { 
        $_.Name -ne ".templates" -and (Test-Path (Join-Path $_.FullName "SKILL.md"))
    }
    foreach ($dir in $skillDirs) {
        $results += Validate-Skill $dir.FullName
    }
}

# Final Summary
Write-Host "`n============================================" -ForegroundColor White
Write-Host "  Summary" -ForegroundColor White
Write-Host "============================================" -ForegroundColor White

$passed = ($results | Where-Object { $_.Status -eq "PASS" }).Count
$failed = ($results | Where-Object { $_.Status -eq "FAIL" }).Count
$skipped = ($results | Where-Object { $_.Status -eq "SKIP" }).Count

Write-Host "  Total skills: $($results.Count)"
Write-Host "  Passed: $passed" -ForegroundColor Green
if ($failed -gt 0) { Write-Host "  Failed: $failed" -ForegroundColor Red }
if ($skipped -gt 0) { Write-Host "  Skipped: $skipped" -ForegroundColor Yellow }

# Output report if requested
if ($OutputReport) {
    $report = @()
    $report += "Skill Reference Integrity Report"
    $report += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $report += "=" * 50
    foreach ($r in $results) {
        $report += ""
        $report += "Skill: $($r.Name)"
        $report += "Status: $($r.Status)"
        $report += "Referenced files: $($r.Referenced.Count)"
        if ($r.Missing.Count -gt 0) {
            $report += "MISSING:"
            foreach ($m in $r.Missing) { $report += "  - $m" }
        }
        if ($r.Orphaned.Count -gt 0) {
            $report += "ORPHANED (on disk, not in SKILL.md):"
            foreach ($o in $r.Orphaned) { $report += "  - $o" }
        }
    }
    $report += ""
    $report += "Summary: $passed passed, $failed failed, $skipped skipped"
    $report | Set-Content $OutputReport
    Write-Host "`n  Report saved to: $OutputReport" -ForegroundColor Green
}
