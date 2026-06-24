---
name: ai-test-report-generation-agent
description: "Consolidate QA plans, results, and healing reports into an Executive QA Report. Trigger to generate a QA report, build executive summary, write test report, or compile release recommendation."
---

# AI Test Report Generation Agent

## Purpose
To compile all testing metrics, healing activities, and requirements analysis into a unified executive QA report, providing quality score indicators and release decisions.

## When to Use
Use this skill when:
- Consolidating all QA requirements, test plans, exploratory findings, execution results, and healing reports into a final executive summary.
- Writing a test report or compiling quality metrics and automation coverage.
- Formulating a release recommendation (Approved, Approved with Risks, Rejected) with risk assessment and quality score indicators.

## Process
1. Gather inputs from previous steps:
   - `specs/requirements.md`
   - `specs/test-plan.md`
   - `specs/exploratory-findings.md`
   - `results/execution-results.md`
   - `results/healing-report.md`
   - `artifacts/screenshots/`
   - `artifacts/logs/`
2. Formulate the Executive QA Report containing:
   - **Executive Summary**: Feature Tested, Environment, Build Information, Date
   - **Test Coverage**: Requirements Covered, Test Cases Executed, Coverage %, Automation Coverage
   - **Execution Summary**: Total, Passed, Failed, Skipped, Blocked, Flaky, Pass %
   - **Defect Summary**: Critical, High, Medium, Low
   - **Self-Healing Summary**: Total Healed, Remaining Failures, Recovery Rate
   - **Quality Assessment**: Risk Level, Quality Score, Production Readiness
   - **Release Recommendation**: APPROVED / APPROVED WITH RISKS / REJECTED (with rationale)
3. Save output files:
   - `test-results/test-report.md`
   - `test-results/test-report.html`

## Output Format
The report must follow the headers below:
```markdown
# EXECUTIVE SUMMARY
# TEST COVERAGE
# EXECUTION SUMMARY
# DEFECT SUMMARY
# SELF-HEALING SUMMARY
# QUALITY ASSESSMENT
# RELEASE RECOMMENDATION
```

## Examples
### Example 1: Release Recommendation Section
```markdown
# RELEASE RECOMMENDATION
**Decision**: APPROVED WITH RISKS
**Rationale**: All functional critical flows passed. 1 medium cosmetic bug remains in the checkout footer, which will be addressed in the next patch.
```

## Edge Cases
- **Missing Inputs**: If some steps didn't produce files, report them as "Not Run" in the summary table and base metrics on available files.
- **Incorrect Pass Rate Calculation**: Ensure pass percentage accounts for skips and blocked cases correctly.