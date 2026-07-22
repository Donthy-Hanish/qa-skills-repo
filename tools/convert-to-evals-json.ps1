<#
.SYNOPSIS
    Convert existing trigger-eval.json and test-prompts.json into evals.json
    for agent-skills-eval.

.DESCRIPTION
    Reads the skill's existing eval files and merges them into the evals.json
    format that agent-skills-eval expects. Run once per skill, or across all skills.

.USAGE
    cd C:\Users\costrategix\PycharmProjects\qa-skills-repo\.agent\skills
    ..\..\tools\convert-to-evals-json.ps1 -SkillName appium-mobile-tester
    ..\..\tools\convert-to-evals-json.ps1   # converts all skills
#>

param(
    [string]$SkillName = ""
)

function Convert-Skill($skillDir) {
    $name = Split-Path $skillDir -Leaf
    $evalsDir = Join-Path $skillDir "evals"
    $triggerFile = Join-Path $evalsDir "trigger-eval.json"
    $promptsFile = Join-Path $evalsDir "test-prompts.json"
    $outputFile = Join-Path $evalsDir "evals.json"

    if (-not (Test-Path $evalsDir)) {
        Write-Host "  [$name] No evals/ directory - skipping" -ForegroundColor Yellow
        return
    }

    $evals = @()
    $evalId = 1

    # Convert test-prompts.json (primary - these have assertions)
    if (Test-Path $promptsFile) {
        $prompts = Get-Content $promptsFile -Raw | ConvertFrom-Json
        foreach ($p in $prompts.evals) {
            $eval = @{
                id = "eval-$evalId"
                name = if ($p.PSObject.Properties["prompt"]) { $p.prompt.Substring(0, [Math]::Min(80, $p.prompt.Length)) + "..." } else { "eval-$evalId" }
                prompt = $p.prompt
                expected_output = if ($p.PSObject.Properties["expected_output"]) { $p.expected_output } else { "" }
                assertions = @()
            }

            # Add expectations as assertions
            if ($p.PSObject.Properties["expectations"]) {
                $eval.assertions = @($p.expectations)
            }

            $evals += $eval
            $evalId++
        }
        Write-Host "  [$name] Converted $($prompts.evals.Count) test prompts" -ForegroundColor Green
    } else {
        Write-Host "  [$name] No test-prompts.json found" -ForegroundColor Yellow
    }

    # Convert trigger-eval.json (should-trigger cases become trigger check evals)
    if (Test-Path $triggerFile) {
        $triggers = Get-Content $triggerFile -Raw | ConvertFrom-Json
        $shouldTrigger = @($triggers.evals | Where-Object { $_.should_trigger -eq $true })
        $shouldNotTrigger = @($triggers.evals | Where-Object { $_.should_trigger -eq $false })

        # Add 2-3 representative should-trigger cases as evals
        $sampleCount = [Math]::Min(3, $shouldTrigger.Count)
        for ($i = 0; $i -lt $sampleCount; $i++) {
            $t = $shouldTrigger[$i]
            $eval = @{
                id = "trigger-$evalId"
                name = "Trigger test: $($t.rationale.Substring(0, [Math]::Min(60, $t.rationale.Length)))"
                prompt = $t.prompt
                expected_output = "The response should demonstrate relevant expertise and provide actionable guidance for this request."
                assertions = @(
                    "The response addresses the specific request rather than asking for clarification on basic concepts",
                    "The response includes concrete technical details relevant to the skill domain"
                )
            }
            $evals += $eval
            $evalId++
        }
        Write-Host "  [$name] Added $sampleCount trigger samples from $($shouldTrigger.Count) should-trigger cases" -ForegroundColor Green
    } else {
        Write-Host "  [$name] No trigger-eval.json found" -ForegroundColor Yellow
    }

    if ($evals.Count -eq 0) {
        Write-Host "  [$name] No evals generated - skipping" -ForegroundColor Yellow
        return
    }

    # Build final structure
    $output = @{
        skill_name = $name
        evals = $evals
    }

    # Write with proper JSON formatting
    $json = $output | ConvertTo-Json -Depth 5
    Set-Content $outputFile -Value $json -Encoding UTF8

    Write-Host "  [$name] Generated evals.json with $($evals.Count) evals at $outputFile" -ForegroundColor Cyan
}

# Main
Write-Host "============================================" -ForegroundColor White
Write-Host "  Evals.json Converter" -ForegroundColor White
Write-Host "============================================" -ForegroundColor White

$basePath = Get-Location

if ($SkillName) {
    $skillDir = Join-Path $basePath $SkillName
    if (Test-Path $skillDir) {
        Convert-Skill $skillDir
    } else {
        Write-Host "Skill not found: $SkillName" -ForegroundColor Red
    }
} else {
    $skillDirs = Get-ChildItem $basePath -Directory | Where-Object {
        $_.Name -ne ".templates" -and (Test-Path (Join-Path $_.FullName "SKILL.md"))
    }
    foreach ($dir in $skillDirs) {
        Convert-Skill $dir.FullName
    }
}

Write-Host "`nDone. Run: npx agent-skills-eval --config agent-skills-eval.yaml" -ForegroundColor Green
