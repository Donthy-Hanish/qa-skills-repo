---
name: playwright-mcp-exploratory-testing-agent
description: "Autonomously navigate web apps using Playwright MCP to run exploratory testing, find UI bugs, and capture browser traces. Trigger when asked to run exploratory testing or perform browser testing."
---

# Playwright MCP Exploratory Testing Agent

## Purpose
To execute manual-style exploratory testing autonomously using Playwright browser automation, searching for bugs, capturing artifacts (screenshots, logs, traces), and recording findings.

## When to Use
Activate this skill when:
- Asked to run exploratory testing or find UI bugs autonomously on a live web application.
- Performing browser testing with Playwright MCP against a staging or production URL.
- Capturing browser traces, console logs, network logs, or screenshots for defect evidence.
- Investigating functional defects, validation issues, accessibility, or responsive design problems.

## Process
1. Open the target application URL (e.g., `https://www.saucedemo.com/`).
2. Refer to the test plan (`specs/test-plan.md`) to guide the coverage.
3. Perform autonomous navigation and exploration.
4. Investigate:
   - 1. Functional defects, 2. Validation issues, 3. Broken links, 4. UI inconsistencies, 5. Accessibility issues, 6. Browser console errors, 7. API failures, 8. Slow loading pages, 9. Network failures, 10. Responsive design issues.
5. Capture artifacts:
   - Screenshots (store in `artifacts/screenshots/`)
   - Browser Traces (store in `artifacts/traces/`)
   - Browser/Network Logs (store in `artifacts/logs/`)
6. Document exploratory findings in `specs/exploratory-findings.md`.

## Output Format
The findings file `specs/exploratory-findings.md` must list:
- Defect ID
- Title
- Description
- Severity
- Priority
- Steps to Reproduce
- Expected Result
- Actual Result
- Screenshot Reference

## Examples
### Example 1
**Defect entry in exploratory-findings.md**:
```markdown
### DEF-01: Password Input Plaintext Exposure
- **Severity**: High
- **Steps**:
  1. Open login page.
  2. Type password.
- **Expected**: Password masked.
- **Actual**: Password displayed in plaintext.
- **Screenshot**: `artifacts/screenshots/def-01.png`
```

## Edge Cases
- **Login Blocked**: If credentials fail, log a critical setup defect and stop execution.
- **Browser Crash**: Save the run logs up to the crash point and record browser crash info.
