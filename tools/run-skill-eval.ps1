<#
.SYNOPSIS
    Run skill evals using Anthropic's Claude API directly.
    Compares with_skill vs without_skill outputs and judges assertions.

.USAGE
    cd C:\Users\costrategix\PycharmProjects\qa-skills-repo\.agent\skills
    $env:ANTHROPIC_API_KEY = "sk-ant-your-key"
    ..\..\tools\run-skill-eval.ps1 -SkillName appium-mobile-tester
    ..\..\tools\run-skill-eval.ps1 -SkillName appium-mobile-tester -Model claude-haiku-4-5-20251001
    ..\..\tools\run-skill-eval.ps1 -SkillName appium-mobile-tester -OutputReport ..\..\eval-reports
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SkillName,
    [string]$Model = "claude-sonnet-4-6",
    [string]$JudgeModel = "claude-haiku-4-5-20251001",
    [string]$OutputReport = ".",
    [int]$MaxTokens = 4096,
    [int]$DelaySeconds = 2
)

$ErrorActionPreference = "Stop"

function Call-Claude($systemPrompt, $userPrompt, $model, $maxTokens) {
    $apiKey = $env:ANTHROPIC_API_KEY
    if (-not $apiKey) {
        throw "ANTHROPIC_API_KEY environment variable not set"
    }

    $body = @{
        model      = $model
        max_tokens = $maxTokens
        messages   = @(
            @{ role = "user"; content = $userPrompt }
        )
    }

    if ($systemPrompt) {
        $body["system"] = $systemPrompt
    }

    $json = $body | ConvertTo-Json -Depth 5
    $headers = @{
        "x-api-key"         = $apiKey
        "anthropic-version" = "2023-06-01"
        "content-type"      = "application/json"
    }

    try {
        $response = Invoke-RestMethod -Uri "https://api.anthropic.com/v1/messages" `
            -Method Post -Headers $headers -Body $json -TimeoutSec 120

        $text = ($response.content | Where-Object { $_.type -eq "text" } | ForEach-Object { $_.text }) -join "`n"
        $inputTokens = $response.usage.input_tokens
        $outputTokens = $response.usage.output_tokens
        return @{ text = $text; input_tokens = $inputTokens; output_tokens = $outputTokens; error = $null }
    }
    catch {
        return @{ text = ""; input_tokens = 0; output_tokens = 0; error = $_.Exception.Message }
    }
}

function Judge-Assertion($output, $assertion, $judgeModel) {
    $judgePrompt = @"
You are an eval judge. Given a model output and an assertion, determine if the assertion is satisfied.

MODEL OUTPUT:
$output

ASSERTION:
$assertion

Respond with ONLY a JSON object (no markdown, no backticks):
{"pass": true/false, "evidence": "one sentence explanation"}
"@

    $result = Call-Claude -systemPrompt $null -userPrompt $judgePrompt -model $judgeModel -maxTokens 200
    if ($result.error) {
        return @{ pass = $false; evidence = "Judge error: $($result.error)" }
    }

    try {
        $clean = $result.text -replace '```json', '' -replace '```', '' | ForEach-Object { $_.Trim() }
        $parsed = $clean | ConvertFrom-Json
        return @{ pass = [bool]$parsed.pass; evidence = $parsed.evidence }
    }
    catch {
        return @{ pass = $false; evidence = "Judge returned unparseable response: $($result.text.Substring(0, [Math]::Min(100, $result.text.Length)))" }
    }
}

# Main
$basePath = Get-Location
$skillDir = Join-Path $basePath $SkillName
$skillMd = Join-Path $skillDir "SKILL.md"
$evalsFile = Join-Path (Join-Path $skillDir "evals") "evals.json"

if (-not (Test-Path $skillMd)) { throw "SKILL.md not found at $skillMd" }
if (-not (Test-Path $evalsFile)) { throw "evals/evals.json not found at $evalsFile" }

$skillContent = Get-Content $skillMd -Raw
$evalsData = Get-Content $evalsFile -Raw | ConvertFrom-Json

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$reportFile = Join-Path $OutputReport "eval-report_${SkillName}_${timestamp}.txt"
$htmlFile = Join-Path $OutputReport "eval-report_${SkillName}_${timestamp}.html"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Skill Eval Runner (Anthropic API)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Skill: $SkillName" -ForegroundColor White
Write-Host "  Target Model: $Model" -ForegroundColor White
Write-Host "  Judge Model: $JudgeModel" -ForegroundColor White
Write-Host "  Evals: $($evalsData.evals.Count)" -ForegroundColor White
Write-Host "  Mode: with_skill vs without_skill" -ForegroundColor White
Write-Host ""

$results = @()
$evalIndex = 0

foreach ($eval in $evalsData.evals) {
    $evalIndex++
    Write-Host "--- Eval $evalIndex/$($evalsData.evals.Count): $($eval.name) ---" -ForegroundColor Yellow

    # Run WITH skill
    Write-Host "  [with_skill] Calling $Model..." -ForegroundColor Gray
    $systemWithSkill = "You have the following skill loaded:`n`n$skillContent`n`nUse this skill to respond to the user's request."
    $withResult = Call-Claude -systemPrompt $systemWithSkill -userPrompt $eval.prompt -model $Model -maxTokens $MaxTokens

    if ($withResult.error) {
        Write-Host "  [with_skill] ERROR: $($withResult.error)" -ForegroundColor Red
    }
    else {
        Write-Host "  [with_skill] OK ($($withResult.output_tokens) tokens)" -ForegroundColor Green
    }

    Start-Sleep -Seconds $DelaySeconds

    # Run WITHOUT skill
    Write-Host "  [without_skill] Calling $Model..." -ForegroundColor Gray
    $withoutResult = Call-Claude -systemPrompt $null -userPrompt $eval.prompt -model $Model -maxTokens $MaxTokens

    if ($withoutResult.error) {
        Write-Host "  [without_skill] ERROR: $($withoutResult.error)" -ForegroundColor Red
    }
    else {
        Write-Host "  [without_skill] OK ($($withoutResult.output_tokens) tokens)" -ForegroundColor Green
    }

    Start-Sleep -Seconds $DelaySeconds

    # Judge assertions
    $withPassed = 0
    $withoutPassed = 0
    $withAssertions = @()
    $withoutAssertions = @()

    foreach ($assertion in $eval.assertions) {
        # Judge with_skill
        Write-Host "  [judge] with_skill: $($assertion.Substring(0, [Math]::Min(60, $assertion.Length)))..." -ForegroundColor Gray
        $withJudge = Judge-Assertion -output $withResult.text -assertion $assertion -judgeModel $JudgeModel
        if ($withJudge.pass) { $withPassed++ }
        $withAssertions += @{ assertion = $assertion; pass = $withJudge.pass; evidence = $withJudge.evidence }
        $icon = if ($withJudge.pass) { [char]0x2713 } else { "X" }
        $color = if ($withJudge.pass) { "Green" } else { "Red" }
        Write-Host "    $icon $($assertion.Substring(0, [Math]::Min(70, $assertion.Length)))" -ForegroundColor $color

        Start-Sleep -Seconds 1

        # Judge without_skill
        $withoutJudge = Judge-Assertion -output $withoutResult.text -assertion $assertion -judgeModel $JudgeModel
        if ($withoutJudge.pass) { $withoutPassed++ }
        $withoutAssertions += @{ assertion = $assertion; pass = $withoutJudge.pass; evidence = $withoutJudge.evidence }

        Start-Sleep -Seconds 1
    }

    $totalAssertions = $eval.assertions.Count
    $withRate = if ($totalAssertions -gt 0) { [math]::Round(($withPassed / $totalAssertions) * 100, 1) } else { 0 }
    $withoutRate = if ($totalAssertions -gt 0) { [math]::Round(($withoutPassed / $totalAssertions) * 100, 1) } else { 0 }
    $delta = $withRate - $withoutRate

    Write-Host "  Result: with_skill $withRate% vs without_skill $withoutRate% (delta: +$delta pp)" -ForegroundColor Cyan
    Write-Host ""

    $results += @{
        id            = $eval.id
        name          = $eval.name
        prompt        = $eval.prompt
        with_skill    = @{
            output     = $withResult.text.Substring(0, [Math]::Min(500, $withResult.text.Length))
            tokens     = $withResult.output_tokens
            passed     = $withPassed
            total      = $totalAssertions
            rate       = $withRate
            assertions = $withAssertions
            error      = $withResult.error
        }
        without_skill = @{
            output     = $withoutResult.text.Substring(0, [Math]::Min(500, $withoutResult.text.Length))
            tokens     = $withoutResult.output_tokens
            passed     = $withoutPassed
            total      = $totalAssertions
            rate       = $withoutRate
            assertions = $withoutAssertions
            error      = $withoutResult.error
        }
        delta         = $delta
    }
}

# Summary
$totalWith = ($results | ForEach-Object { $_.with_skill.passed } | Measure-Object -Sum).Sum
$totalWithout = ($results | ForEach-Object { $_.without_skill.passed } | Measure-Object -Sum).Sum
$totalAsserts = ($results | ForEach-Object { $_.with_skill.total } | Measure-Object -Sum).Sum
$overallWithRate = if ($totalAsserts -gt 0) { [math]::Round(($totalWith / $totalAsserts) * 100, 1) } else { 0 }
$overallWithoutRate = if ($totalAsserts -gt 0) { [math]::Round(($totalWithout / $totalAsserts) * 100, 1) } else { 0 }
$overallDelta = $overallWithRate - $overallWithoutRate

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  SUMMARY: $SkillName" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  with_skill:    $overallWithRate% ($totalWith/$totalAsserts assertions passed)" -ForegroundColor Green
Write-Host "  without_skill: $overallWithoutRate% ($totalWithout/$totalAsserts assertions passed)" -ForegroundColor Yellow
Write-Host "  Delta:         +$overallDelta percentage points" -ForegroundColor Cyan
Write-Host ""

# Generate HTML report
$htmlRows = ""
foreach ($r in $results) {
    $withColor = if ($r.with_skill.rate -ge 80) { "#4CAF50" } elseif ($r.with_skill.rate -ge 50) { "#FF9800" } else { "#F44336" }
    $withoutColor = if ($r.without_skill.rate -ge 80) { "#4CAF50" } elseif ($r.without_skill.rate -ge 50) { "#FF9800" } else { "#F44336" }
    $deltaColor = if ($r.delta -gt 0) { "#4CAF50" } elseif ($r.delta -eq 0) { "#FF9800" } else { "#F44336" }

    $withDetails = ""
    foreach ($a in $r.with_skill.assertions) {
        $aIcon = if ($a.pass) { "&#10003;" } else { "&#10007;" }
        $aColor = if ($a.pass) { "#4CAF50" } else { "#F44336" }
        $withDetails += "<div style='margin:2px 0;color:$aColor'>$aIcon $($a.assertion)</div><div style='margin-left:20px;font-size:12px;color:#888'>$($a.evidence)</div>"
    }

    $withoutDetails = ""
    foreach ($a in $r.without_skill.assertions) {
        $aIcon = if ($a.pass) { "&#10003;" } else { "&#10007;" }
        $aColor = if ($a.pass) { "#4CAF50" } else { "#F44336" }
        $withoutDetails += "<div style='margin:2px 0;color:$aColor'>$aIcon $($a.assertion)</div><div style='margin-left:20px;font-size:12px;color:#888'>$($a.evidence)</div>"
    }

    $htmlRows += @"
    <tr>
        <td style='padding:12px;border:1px solid #ddd;vertical-align:top;font-weight:bold'>$($r.name)</td>
        <td style='padding:12px;border:1px solid #ddd;vertical-align:top;text-align:center'><span style='font-size:24px;font-weight:bold;color:$withColor'>$($r.with_skill.rate)%</span><br>$($r.with_skill.passed)/$($r.with_skill.total)<br><details><summary>Details</summary>$withDetails</details></td>
        <td style='padding:12px;border:1px solid #ddd;vertical-align:top;text-align:center'><span style='font-size:24px;font-weight:bold;color:$withoutColor'>$($r.without_skill.rate)%</span><br>$($r.without_skill.passed)/$($r.without_skill.total)<br><details><summary>Details</summary>$withoutDetails</details></td>
        <td style='padding:12px;border:1px solid #ddd;vertical-align:top;text-align:center'><span style='font-size:24px;font-weight:bold;color:$deltaColor'>+$($r.delta)pp</span></td>
    </tr>
"@
}

$html = @"
<!DOCTYPE html>
<html>
<head><title>Skill Eval Report - $SkillName</title></head>
<body style='font-family:Calibri,sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f9f9f9'>
<h1 style='color:#1B2A4A'>Skill Eval Report</h1>
<h2 style='color:#2B5797'>$SkillName</h2>
<p style='color:#666'>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | Target: $Model | Judge: $JudgeModel</p>
<div style='background:#fff;border-radius:8px;padding:20px;margin:20px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)'>
<h3>Overall Summary</h3>
<table style='width:100%;border-collapse:collapse'>
<tr><td style='padding:8px'><strong>with_skill</strong></td><td style='font-size:28px;font-weight:bold;color:#4CAF50'>$overallWithRate%</td><td>$totalWith / $totalAsserts assertions passed</td></tr>
<tr><td style='padding:8px'><strong>without_skill</strong></td><td style='font-size:28px;font-weight:bold;color:#FF9800'>$overallWithoutRate%</td><td>$totalWithout / $totalAsserts assertions passed</td></tr>
<tr><td style='padding:8px'><strong>Delta</strong></td><td style='font-size:28px;font-weight:bold;color:#2B5797'>+${overallDelta}pp</td><td>Improvement from skill</td></tr>
</table>
</div>
<h3>Per-Eval Results</h3>
<table style='width:100%;border-collapse:collapse;background:#fff'>
<tr style='background:#1B2A4A;color:#fff'><th style='padding:12px;text-align:left'>Eval</th><th style='padding:12px'>With Skill</th><th style='padding:12px'>Without Skill</th><th style='padding:12px'>Delta</th></tr>
$htmlRows
</table>
<p style='color:#999;margin-top:40px;text-align:center'>CoStrategix QA Skills Repository | Agent Skills Eval | Anthropic API</p>
</body></html>
"@

$html | Set-Content $htmlFile -Encoding UTF8
Write-Host "  HTML Report: $htmlFile" -ForegroundColor Green

# Text report
$reportLines = @()
$reportLines += "Skill Eval Report: $SkillName"
$reportLines += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$reportLines += "Target: $Model | Judge: $JudgeModel"
$reportLines += "=" * 60
$reportLines += ""
$reportLines += "OVERALL: with_skill $overallWithRate% vs without_skill $overallWithoutRate% (delta: +$overallDelta pp)"
$reportLines += ""
foreach ($r in $results) {
    $reportLines += "--- $($r.name) ---"
    $reportLines += "  with_skill: $($r.with_skill.rate)% ($($r.with_skill.passed)/$($r.with_skill.total))"
    $reportLines += "  without_skill: $($r.without_skill.rate)% ($($r.without_skill.passed)/$($r.without_skill.total))"
    $reportLines += "  delta: +$($r.delta) pp"
    $reportLines += ""
}
$reportLines | Set-Content $reportFile -Encoding UTF8
Write-Host "  Text Report: $reportFile" -ForegroundColor Green
