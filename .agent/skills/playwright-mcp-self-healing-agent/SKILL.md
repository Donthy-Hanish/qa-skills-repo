---
name: playwright-mcp-self-healing-agent
description: "Analyze failed Playwright tests and self-heal locator, timing, and assertion failures. Re-runs healed tests and generates results/healing-report.md. Trigger when tests fail or to heal scripts."
---

# Playwright MCP Self-Healing Agent

## Purpose
To automatically diagnose test failures, repair code locators or waits, and verify fixes by re-running failed tests, keeping the suite green and stable.

## When to Use
Activate this skill when:
- Playwright tests are failing on locators, timing issues, or assertion errors and need automated repair.
- Asked to heal test scripts, run self-healing, or resolve flaky test failures.
- Re-running a failed test suite after applying locator or synchronization fixes.
- Generating a esults/healing-report.md summarizing root causes and fixes applied.

## Process
1. Read execution findings from `results/execution-results.md` to identify failed tests.
2. Group failures into categories:
   - A. Locator Changes
   - B. Timing Issues
   - C. Dynamic Elements
   - D. Data Problems
   - E. Assertion Failures
   - F. Environment Issues
3. For each failed test:
   - Determine root cause of failure.
   - Suggest and apply healing techniques.
4. Healing Techniques:
   - **Locator Healing**: Re-discover element in DOM. Follow priority standard (data-testid, aria-label, roles). Update selectors.
   - **Synchronization Healing**: Replace hard sleep waits with smart dynamic waits.
   - **Assertion Healing**: Validate if application logic changed. Update assertions if correct.
   - **Data Healing**: Generate fresh test data.
5. Re-run healed tests.
6. Generate a summary report in `results/healing-report.md`.
7. Save updated script files in `results/healed-tests/`.

## Output Format
Report saved to `results/healing-report.md` containing:
- Original Failure
- Root Cause
- Fix Applied
- Re-Execution Result

## Examples
### Example 1
**results/healing-report.md excerpt**:
```markdown
# Self-Healing Report
- **Failed Test**: `tests/checkout.spec.py`
- **Error**: Locator standard violation. Selector `button.blue` was missing.
- **Healed Action**: Switched selector to standard locator: `css=[data-testid="submit-order"]`.
- **Status**: PASSED on re-execution.
```

## Edge Cases
- **Unhealable Bug**: If failure is due to a functional defect in the application, do NOT heal the script. Log it as a verified bug in `results/healing-report.md`.
- **Infinite Loop**: Set a maximum retry limit of 1 self-healing attempt per locator.
