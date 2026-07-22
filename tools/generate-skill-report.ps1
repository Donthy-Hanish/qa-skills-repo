<#
.SYNOPSIS
    Run all 4 Agent Skills CLI checks across all skills and generate a shareable report.

.DESCRIPTION
    Runs skills validate, skills score --verbose, skills test, and skills sandbox
    for every skill in the repository. Captures all output into a timestamped
    report file suitable for sharing with stakeholders.

.USAGE
    cd C:\Users\costrategix\PycharmProjects\qa-skills-repo\.agent\skills
    .\generate-skill-report.ps1
    .\generate-skill-report.ps1 -SkillName appium-mobile-tester
    .\generate-skill-report.ps1 -OutputDir .\reports
#>

param(
    [string]$SkillName = "",
    [string]$OutputDir = "."
)

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$reportFile = Join-Path $OutputDir "skill-validation-report_$timestamp.txt"

function Log($text) {
    $text | Tee-Object -FilePath $reportFile -Append
}

# Header
Log "================================================================"
Log "  AGENT SKILLS - FULL VALIDATION REPORT"
Log "  Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Log "  Repository: qa-skills-repo"
Log "  CLI Tool: Agent Skills CLI (agentskills.io)"
Log "================================================================"
Log ""

$basePath = Get-Location

# Discover skills
if ($SkillName) {
    $skillDirs = @(Get-Item (Join-Path $basePath $SkillName))
} else {
    $skillDirs = Get-ChildItem $basePath -Directory | Where-Object {
        $_.Name -ne ".templates" -and (Test-Path (Join-Path $_.FullName "SKILL.md"))
    }
}

$summaryTable = @()

foreach ($dir in $skillDirs) {
    $name = $dir.Name
    Log "================================================================"
    Log "  SKILL: $name"
    Log "================================================================"
    Log ""

    # 1. Validate
    Log "--- 1. skills validate ---"
    $validateOutput = & skills validate ".\$name" 2>&1 | Out-String
    Log $validateOutput

    # 2. Score
    Log "--- 2. skills score --verbose ---"
    $scoreOutput = & skills score ".\$name" --verbose 2>&1 | Out-String
    Log $scoreOutput

    # Extract overall score from output
    $scoreMatch = [regex]::Match($scoreOutput, '(\d+)/100\s+(A\+|A|B|C|D|F)')
    $score = if ($scoreMatch.Success) { "$($scoreMatch.Groups[1].Value)/100 $($scoreMatch.Groups[2].Value)" } else { "N/A" }

    # 3. Test
    Log "--- 3. skills test ---"
    $testOutput = & skills test ".\$name" 2>&1 | Out-String
    Log $testOutput

    # Extract test result
    $testMatch = [regex]::Match($testOutput, '(\d+)%')
    $testScore = if ($testMatch.Success) { "$($testMatch.Groups[1].Value)%" } else { "N/A" }

    # 4. Sandbox
    Log "--- 4. skills sandbox ---"
    $sandboxOutput = & skills sandbox ".\$name" 2>&1 | Out-String
    Log $sandboxOutput

    # Extract token count
    $tokenMatch = [regex]::Match($sandboxOutput, 'Tokens:\s+(\d+)')
    $tokens = if ($tokenMatch.Success) { $tokenMatch.Groups[1].Value } else { "N/A" }

    # Extract sandbox grade
    $gradeMatch = [regex]::Match($sandboxOutput, 'Grade:\s+(\w+)\s+\((\d+)%\)')
    $sandboxGrade = if ($gradeMatch.Success) { "$($gradeMatch.Groups[1].Value) ($($gradeMatch.Groups[2].Value)%)" } else { "N/A" }

    $summaryTable += [PSCustomObject]@{
        Skill = $name
        Score = $score
        Test = $testScore
        Sandbox = $sandboxGrade
        Tokens = $tokens
    }

    Log ""
}

# Summary Table
Log "================================================================"
Log "  SUMMARY"
Log "================================================================"
Log ""
Log ("{0,-30} {1,-15} {2,-10} {3,-15} {4,-10}" -f "Skill", "Score", "Test", "Sandbox", "Tokens")
Log ("{0,-30} {1,-15} {2,-10} {3,-15} {4,-10}" -f "-----", "-----", "----", "-------", "------")
foreach ($row in $summaryTable) {
    Log ("{0,-30} {1,-15} {2,-10} {3,-15} {4,-10}" -f $row.Skill, $row.Score, $row.Test, $row.Sandbox, $row.Tokens)
}

Log ""
Log "Report saved to: $reportFile"

Write-Host "`nReport generated: $reportFile" -ForegroundColor Green
