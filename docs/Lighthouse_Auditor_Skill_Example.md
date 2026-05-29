# Lighthouse Auditor Skill - How It Works (Example)

## The Problem

Running Lighthouse audits manually is disconnected from your test suite. Someone has to remember to run it, read the report, and tell the team. If they forget, performance regressions ship to production unnoticed.

## The Solution

The lighthouse-auditor skill generates Lighthouse audit scripts automatically when you describe what you need in plain English. It integrates directly with Robot Framework so performance and accessibility checks run alongside your functional tests.

---

## Example: End-to-End Flow

### Step 1 - You ask in Antigravity

```
Write robot framework tests to audit our staging site
https://staging.ourapp.com for performance and accessibility.
Login page is /login with fields id:email and id:password.
Check homepage, dashboard, and checkout page. Performance
must be above 80, accessibility above 90, LCP under 2.5 seconds.
```

### Step 2 - The skill generates three files

The agent reads the lighthouse-auditor SKILL.md, identifies "user wants Robot Framework", reads templates from the references/ folder, and produces customized files.

**File 1: tests/libraries/LighthouseKeywords.py** (Python keyword library)

```python
class LighthouseKeywords:

    @keyword("Run Lighthouse Audit")
    def run_lighthouse_audit(self, url, preset="desktop"):
        # Runs npx lighthouse via subprocess
        # Returns parsed JSON report

    @keyword("Assert Performance Score")
    def assert_performance_score(self, audit_result, min_score):
        # Extracts performance score and asserts against threshold

    @keyword("Run Authenticated Lighthouse Audit")
    def run_authenticated_lighthouse_audit(self, url, login_url, username, password):
        # Logs in via Playwright, extracts cookies
        # Passes cookies to Lighthouse via --extra-headers
        # Audits the authenticated page
```

**File 2: tests/variables/variables.robot** (environment config)

```robot
*** Variables ***
${BASE_URL}           https://staging.ourapp.com
${LOGIN_URL}          https://staging.ourapp.com/login
${USERNAME}           testuser
${PASSWORD}           password123
${MIN_PERF_SCORE}     80
${MIN_A11Y_SCORE}     90
${MAX_LCP_MS}         2500
```

**File 3: tests/lighthouse_audit.robot** (test suite)

```robot
*** Settings ***
Library           libraries/LighthouseKeywords.py
Variables         variables/variables.robot
Force Tags        performance    lighthouse

*** Test Cases ***
Homepage Performance Check
    [Tags]    smoke
    ${result}=    Run Lighthouse Audit    ${BASE_URL}
    Assert Performance Score    ${result}    ${MIN_PERF_SCORE}
    Assert Accessibility Score    ${result}    ${MIN_A11Y_SCORE}

Dashboard Authenticated Audit
    [Tags]    regression
    ${result}=    Run Authenticated Lighthouse Audit    ${BASE_URL}/dashboard
    ...    login_url=${LOGIN_URL}    username=${USERNAME}    password=${PASSWORD}
    Assert Performance Score    ${result}    ${MIN_PERF_SCORE}
    Assert LCP Under Threshold    ${result}    ${MAX_LCP_MS}

Checkout Page Accessibility
    [Tags]    regression    critical
    ${result}=    Run Authenticated Lighthouse Audit    ${BASE_URL}/checkout
    ...    login_url=${LOGIN_URL}    username=${USERNAME}    password=${PASSWORD}
    Assert Accessibility Score    ${result}    ${MIN_A11Y_SCORE}
```

### Step 3 - You run the tests

```bash
# Run all lighthouse tests
robot tests/lighthouse_audit.robot

# Or just smoke tests
robot --include smoke tests/lighthouse_audit.robot

# Or include in your full regression suite alongside functional tests
robot tests/
```

### Step 4 - Results in your existing reports

```
robot tests/
  Login test              Pass
  Cart test               Pass
  Homepage Performance    Pass  (score: 88, threshold: 80)
  Dashboard Audit         FAIL  (score: 62, threshold: 80)
  Checkout Accessibility  Pass  (score: 94, threshold: 90)

BUILD FAILED - performance regression caught before deploy
```

---

## How It Works Internally

```
You describe what you need in plain English
        |
Skill reads templates from references/
        |
Agent generates customized .robot + .py + variables
        |
You run: robot tests/
        |
Lighthouse audits run as Robot Framework test cases
        |
Results appear in the same report.html your team already reads
```

---

## What the Skill Covers

| Capability | Description |
|---|---|
| Standalone Python audit | Quick one-off scripts for single or batch URL audits |
| Robot Framework integration | .robot + .py keyword library for test suite integration |
| CI/CD configuration | lighthouserc.json + GitHub Actions / Jenkins pipeline |
| Before/after comparison | Score diff reports between two audit runs |
| Authenticated page audits | Login via Playwright, cookie injection, audit behind auth |
| User flows (navigation) | Cold load + warm load comparison in one report |
| User flows (snapshot) | Audit page state (modal open, form filled) without reload |
| User flows (timespan) | Measure CLS/TBT during scroll, click, type interactions |

## Skill Quality

| Metric | Value |
|---|---|
| Agent Skills CLI Score | 100/100 A+ |
| Test prompts | 8 covering all capabilities |
| Trigger eval queries | 20 (10 should-trigger, 10 near-miss should-not) |
| Reference files | 6 (playbook, advanced patterns, templates, user flows) |
| Scripts | 1 (run_lighthouse.py) |
