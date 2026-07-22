---
name: lighthouse-auditor
description: "Runs Google Lighthouse audits. Generates Python/Robot scripts and configures CI/CD. Use for performance, accessibility, SEO, or LCP/CLS audits. Do not use for general functional UI testing."
---

# Lighthouse Auditor

## Purpose
Automate and validate web page quality audits by generating scripts, configuring CI/CD pipelines, and integrating metric thresholds into test suites to capture regressions early.

## When to Use
Use this skill when:
- Creating or editing scripts to perform Google Lighthouse audits on single or multiple URLs.
- Auditing authenticated pages behind login gates or multi-step user interaction flows (User Flows).
- Setting up custom performance thresholds or budgets for Core Web Vitals (LCP, FID/INP, CLS, TBT, Speed Index).
- Integrating Lighthouse performance testing with the Robot Framework.
- Configuring Lighthouse CI (`lighthouserc.json`) for Jenkins or GitHub Actions pipelines.
- Differentiating and comparing before/after audit scores.

Do NOT use this skill for:
- Writing standard Selenium or Playwright functional test suites.
- Debugging general front-end functional errors.
- Testing REST API schemas and contracts.

## Process
1. **Identify User Intent**:
   - IF the user wants a single/batch audit script -> Generate a Python subprocess script wrapping the Lighthouse CLI.
   - IF the user wants CI/CD integration -> Generate a `lighthouserc.json` and workflow YAML (e.g. GitHub Actions).
   - IF the user wants Robot Framework -> Generate a `.robot` test case file and a supporting Python library for keywords.
   - IF the user wants to compare audits -> Generate a before/after Python comparison script.
   - IF the user wants to audit a page behind login -> Generate an authenticated audit (using cookie injection) or a Puppeteer/Playwright user flow script.
   - IF the user wants to test cached/repeat-visit performance -> Use warm navigation with `disableStorageReset: true` and compare against a cold load.
   - IF the user wants to audit a specific page state (form filled, modal open, panel expanded) -> Use snapshot mode (`flow.snapshot()`) which tests the current DOM without reloading.
   - IF the user wants to measure metrics during user interactions (scroll, click, type) -> Use timespan mode (`flow.startTimespan()` / `flow.endTimespan()`).
2. **Apply Presets & Configuration**:
   - Determine target environment (mobile vs desktop) and set correct presets (Lighthouse uses mobile by default, desktop requires `--preset=desktop`).
   - Use headless Chrome flags (`--headless`, `--no-sandbox`, `--disable-gpu`) for reliability in headless or CI environments.
3. **Configure Thresholds & Budgets**:
   - Define minimum acceptable scores (0-100) for categories (Performance, Accessibility, Best Practices, SEO).
   - Assert limits for Core Web Vitals: LCP (Largest Contentful Paint), FID/INP (First Input Delay / Interaction to Next Paint), CLS (Cumulative Layout Shift), TBT (Total Blocking Time), and SI (Speed Index).
4. **Reference Resources**:
   - Refer to `references/playbook.md` for CLI options, thresholds, and error troubleshooting.
   - Refer to `references/advanced-patterns.md` for custom audits, budgets, and trends.
   - Refer to `scripts/run_lighthouse.py` for the pre-implemented Python utility.
   - Refer to `references/lighthouse-keywords.py` for the custom keyword library.
   - Refer to `references/lighthouse-audit-template.robot` for the test template.
   - Refer to `references/user-flow-templates.js` for cold+warm, snapshot, and timespan flow examples.
   - Refer to `references/user-flow-example.js` for a complete working user flow script.

---

## Output Format

### Python Subprocess Audit Template
```python
import subprocess
import json
import sys

def run_audit(url, output_json):
    # npx lighthouse is the standard CLI runner
    cmd = ["npx", "lighthouse", url, "--output=json", f"--output-path={output_json}", "--chrome-flags='--headless --no-sandbox'"]
    # Handle Windows command prompt resolution via shell=True
    subprocess.run(cmd, shell=(sys.platform == "win32"), check=True)
```

### Robot Framework Integration Template
```robot
*** Settings ***
Library           LighthouseKeywords.py
Suite Teardown    Close All Browsers

*** Test Cases ***
Verify Page Performance And Quality
    [Documentation]    Runs a Lighthouse audit and asserts target scores.
    ${metrics}=    Run Lighthouse Audit    https://example.com    preset=desktop
    Assert Performance Score    ${metrics}    80
    Assert Accessibility Score    ${metrics}    90
    Extract Core Web Vitals    ${metrics}
```

---

## Examples

### Example 1: Creating a Python Batch Auditor
**User Prompt**: "Write a Python script that runs Lighthouse audits for list of URLs and fails if performance score drops below 85."
**Response**:
```python
import os
import sys
import json
import subprocess

def audit_url(url, min_perf=85):
    report_name = "lh_report"
    cmd = ["npx", "lighthouse", url, "--output=json", f"--output-path=./{report_name}", "--chrome-flags='--headless'"]
    subprocess.run(cmd, shell=(sys.platform == "win32"), check=True)
    
    with open(f"./{report_name}.report.json", "r") as f:
        report = json.load(f)
        
    score = report["categories"]["performance"]["score"] * 100
    print(f"Performance Score for {url}: {score}")
    if score < min_perf:
        raise ValueError(f"Performance score {score} is below threshold {min_perf}")

if __name__ == "__main__":
    urls = ["https://example.com", "https://google.com"]
    for url in urls:
        audit_url(url)
```

### Example 2: Configuring lighthouserc.json
**User Prompt**: "Help me configure a lighthouserc.json to check performance and accessibility in CI."
**Response**:
```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "url": ["https://example.com/"],
      "settings": {
        "preset": "desktop"
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.85}],
        "categories:accessibility": ["error", {"minScore": 0.90}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 2500}]
      }
    }
  }
}
```

### Example 3: Authenticated Audit Script
**User Prompt**: "Write a python script that logs in to https://example.com/login with credentials and then runs a Lighthouse audit on https://example.com/dashboard."
**Response**:
```python
import json
import os
import subprocess
import sys
from playwright.sync_api import sync_playwright

def run_authenticated_audit():
    # 1. Login and extract session cookies
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://example.com/login")
        page.fill("#username", "myuser")
        page.fill("#password", "mypassword")
        page.click("#submit")
        page.wait_for_load_state("networkidle")
        cookies = context.cookies()
        browser.close()
        
    # 2. Format cookies for HTTP header injection
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    headers = json.dumps({"Cookie": cookie_str})
    
    # 3. Invoke Lighthouse with custom headers
    cmd = [
        "npx", "lighthouse", "https://example.com/dashboard",
        "--output=json",
        "--output-path=./dashboard_report",
        f"--extra-headers={headers}",
        "--chrome-flags='--headless'"
    ]
    subprocess.run(cmd, shell=(sys.platform == "win32"), check=True)
    print("Authenticated audit report generated successfully.")
```

---

## Edge Cases

- **Local Host/Dev Testing**: If testing `http://localhost`, Chrome might block HTTPS validation audits. Disable HTTPS-related audits or configure Lighthouse to ignore SSL warnings.
- **Authentication**: Sites requiring login will show scores for the login page unless you run custom Chrome instances, share session cookies, or use Puppeteer/Playwright scripts to pre-authenticate the browser before passing control to Lighthouse.
- **Network Fluctuation**: Performance audits can be flaky in CI. Mitigate by running the audit multiple times (e.g. `numberOfRuns: 3` in LHCI) and taking the median or average score.

---

## Anti-patterns

- **Testing with Extensions Enabled**: Running audits in a browser with active extensions will skew metrics. Always run with a clean, headless profile.
- **Not Using Headless Mode**: Running audits with visible browsers is slower and less reproducible. Use headless execution flags.
- **Testing on Dev Server**: Running tests against dev servers (with raw source files, HMR active, and unminified bundles) will report inaccurate scores. Always run audits on production-like Staging environments.
- **Ignoring Throttling Settings**: Not specifying throttling methods leads to inconsistent results between developer machines. Always define throttling parameters.

---

## Reference Files

| File | What it is | When to load |
|---|---|---|
| `references/playbook.md` | CLI options, thresholds, and error troubleshooting guide | When configuring audit parameters or debugging CLI errors |
| `references/advanced-patterns.md` | Custom audits, performance budgets, and trend tracking | When the user needs budgets, multi-run trends, or custom audit categories |
| `references/lighthouse-keywords.py` | Custom Robot Framework keyword library for Lighthouse | When generating Robot Framework integration tests |
| `references/lighthouse-audit-template.robot` | Robot Framework test suite template | When the user wants a ready-to-run .robot file |
| `references/user-flow-templates.js` | Puppeteer user flow templates for cold+warm, snapshot, and timespan modes | When auditing authenticated pages, SPAs, or specific page states |
| `references/user-flow-example.js` | Complete working user flow script with login and navigation | When the user needs a full end-to-end example of an authenticated user flow audit |

## Scripts

| Script | Purpose | When to run |
|---|---|---|
| `scripts/run_lighthouse.py` | Pre-implemented Python utility wrapping the Lighthouse CLI with threshold assertions | Step 1, when the user wants a ready-to-use audit script |

---

## Changelog
- **v1.0.0**: Initial release of the `lighthouse-auditor` skill.
