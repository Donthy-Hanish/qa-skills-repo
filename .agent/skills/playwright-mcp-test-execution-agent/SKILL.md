---
name: playwright-mcp-test-execution-agent
description: >
   Execute Playwright test suites across browsers, capture results and artifacts, and generate execution reports.
---

# Playwright MCP Test Execution Agent

## Purpose
To execute the automated test suites on multiple browsers, measure test performance, gather execution artifacts, and generate a summary report.

## When to Use
Use this skill when:
- Executing Playwright test suites.
- Running regression, smoke, or sanity automation suites.
- Validating application behavior across Chromium, Firefox, and WebKit.
- Capturing screenshots, videos, traces, and execution metrics.
- Generating automated execution reports for QA sign-off.
- Investigating test failures and collecting debugging artifacts.
- Running `npx playwright test` or similar automated test commands.

## Process
1. Identify all tests to run (e.g. inside `tests/` directory).
2. Execute the test command, for example:
   `npx playwright test` or `pytest`
3. Execute the tests across:
   - Chromium
   - Firefox
   - WebKit
4. Capture results and run artifacts:
   - Pass/Fail metrics
   - Execution time
   - Screenshots
   - Videos
   - Traces
5. Generate the execution results summary in `results/execution-results.md`.

## Output Format
A summary saved in `results/execution-results.md` that lists:
- Total Tests Executed
- Passed Tests
- Failed Tests
- Execution Duration
- Failed test details and browser logs.

## Examples
### Example 1
**results/execution-results.md content**:
```markdown
# Execution Results
- **Date**: 2026-06-23
- **Total Tests**: 10
- **Pass Rate**: 90% (9 Passed, 1 Failed)

## Failed Tests
1. `tests/checkout.spec.py` - TimeoutError: Locator "css=[data-testid=submit-order]" not found.
```

## Edge Cases
- **Execution Crash**: If dependencies are missing or compilation fails, report execution block immediately.
- **Port Conflict**: Handle port conflicts when launching test servers dynamically.
