# Lighthouse Audit Setup & Integration Playbook

This playbook provides a comprehensive guide for QA engineers to set up, run, troubleshoot, and integrate Google Lighthouse audits within the automated testing workflow.

---

## 1. Installation & Environment Setup

Lighthouse requires Node.js (version 18+ recommended) and Google Chrome or a Chromium-based browser.

### Local Installation
To avoid global dependency clutter, run Lighthouse using `npx`:
```bash
# Verify npx is installed and running the latest lighthouse CLI
npx lighthouse --version
```
Or install it as a development dependency in your project:
```bash
npm install --save-dev lighthouse
```

### Global Installation (Optional)
```bash
npm install -g lighthouse
```

### Subprocess / Python Prep
If invoking via python, ensure `npx` is available in your shell's `PATH`. If running on Windows, the subprocess execution must use `shell=True` to resolve `npx` (which resolves to `npx.cmd`).

---

## 2. Standard CLI Commands & Options

Here are the most common Lighthouse CLI flags used for QA automation:

| Flag | Purpose | Example |
|---|---|---|
| `--output` | Format of output (json, html, csv) | `--output=json --output=html` |
| `--output-path` | Output path base name | `--output-path=./reports/home` |
| `--preset` | Use preconfigured settings | `--preset=desktop` (mobile is default) |
| `--chrome-flags` | Custom flags passed to Chrome | `--chrome-flags="--headless --no-sandbox"` |
| `--config-path` | Custom configuration file | `--config-path=./custom-config.js` |
| `--only-categories` | Limit audit categories | `--only-categories=performance,accessibility` |

### Running a Headless Desktop Audit
```bash
npx lighthouse https://example.com --preset=desktop --chrome-flags="--headless" --output=json --output=html --output-path=./reports/desktop_audit
```

---

## 3. Metric Thresholds & Classifications

Core Web Vitals and scoring categories are classified into three bands by Google:

### Category Scores (Performance, Accessibility, Best Practices, SEO)
- **Good (Green)**: 90 - 100
- **Needs Improvement (Orange)**: 50 - 89
- **Poor (Red)**: 0 - 49

### Core Web Vitals (Threshold Values)
When establishing quality gates, align your thresholds with these industry-standard ranges:

| Metric | Code | Good (Green) | Needs Improvement (Orange) | Poor (Red) |
|---|---|---|---|---|
| **Largest Contentful Paint** | `largest-contentful-paint` | <= 2.5s (2500ms) | > 2.5s and <= 4.0s | > 4.0s (4000ms) |
| **First Input Delay** | `max-potential-fid` | <= 100ms | > 100ms and <= 300ms | > 300ms |
| **Interaction to Next Paint** | `interaction-to-next-paint` | <= 200ms | > 200ms and <= 500ms | > 500ms |
| **Cumulative Layout Shift** | `cumulative-layout-shift` | <= 0.10 | > 0.10 and <= 0.25 | > 0.25 |
| **Total Blocking Time** | `total-blocking-time` | <= 300ms | > 300ms and <= 600ms | > 600ms |
| **Speed Index** | `speed-index` | <= 3.4s (3400ms) | > 3.4s and <= 5.8s | > 5.8s (5800ms) |

---

## 4. Debugging Common Lighthouse Errors

### 1. Chrome Connection Timeout
* **Symptom**: `Lighthouse failed with exit code 1. Error: Connect to Chrome timeout.`
* **Cause**: Chrome didn't start in time or the port was blocked.
* **Resolution**:
  - Run Chrome in headless mode with `--no-sandbox` and `--disable-gpu` flags.
  - If running in Docker, ensure you are running on a Debian/Ubuntu image with Chrome installed and using `--disable-dev-shm-usage`.

### 2. Page Load Failures (NO_DOCUMENT_REQUEST)
* **Symptom**: `Lighthouse failed: NO_DOCUMENT_REQUEST. Lighthouse was unable to reliably load the page.`
* **Cause**: DNS resolution failed, the site requires authentication, or the site blocked the requests (bot detection).
* **Resolution**:
  - Verify that the URL is reachable from the execution machine.
  - Set a custom User-Agent to bypass simple firewalls:
    `--chrome-flags="--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...'"`
  - Ensure any self-signed certificates are ignored: `--chrome-flags="--ignore-certificate-errors"`

### 3. Protocol Errors (e.g. `PAGE_HUNG`)
* **Symptom**: `Lighthouse failed: PAGE_HUNG. The page took too long to load.`
* **Cause**: Heavy scripts or infinite loops prevent the page from firing its load events.
* **Resolution**:
  - Increase the timeout limits.
  - Check if the site runs correctly under standard Chrome execution.

---

## 5. CI/CD Integration Patterns

Integrating Lighthouse into CI pipelines ensures performance regressions are caught before they reach production.

### GitHub Actions Integration (Lighthouse CI)
Create a `.github/workflows/lighthouse.yml` pipeline:

```yaml
name: Performance Audits
on: [push, pull_request]

jobs:
  lighthouse:
    runs-ok: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18

      - name: Install Lighthouse CI CLI
        run: npm install -g @lhci/cli@0.12.x

      - name: Run Lighthouse CI Audit
        run: lhci autorun
```

### Jenkins Pipeline Integration
Run the python wrapper script or CLI directly as a build step in your `Jenkinsfile`:

```groovy
pipeline {
    agent any
    stages {
        stage('Audit Performance') {
            steps {
                sh 'npx lighthouse https://staging.example.com --preset=desktop --chrome-flags="--headless --no-sandbox" --output=json --output-path=./lighthouse-report'
                // Run verification / threshold check
                sh 'python3 .agent/skills/lighthouse-auditor/scripts/run_lighthouse.py audit --url https://staging.example.com --preset desktop'
            }
        }
    }
}
```

---

## 6. Authenticated Audits and User Flows

Testing pages behind authentication gates requires passing credentials or session tokens to the browser. Lighthouse offers two main approaches: Cookie Injection (Authenticated Audits) and User Flows.

### Cookie Injection vs. User Flows

| Feature | Cookie Injection (Authenticated Audits) | Lighthouse User Flows (Puppeteer/Playwright) |
|---|---|---|
| **What it is** | Authenticate once, extract session cookies, inject them via `--extra-headers` for the target URL. | Programmatically launch Chrome, interact with the page, and record audits dynamically. |
| **Best Used For** | Simple dashboard pages, static pages behind login gates. | Multi-step user checkout processes, SPA state changes, custom interactions. |
| **Complexity** | Low (no code changes, uses CLI flags). | High (requires writing a Node/Python automation script). |
| **Limitations** | Session must be valid from a cookie alone (no session storage or IndexedDB dependencies). | Requires keeping browser versions aligned with Lighthouse dependencies. |

### Finding the Right CSS Selectors
For automated login forms, use Chrome DevTools (right-click -> Inspect) to find stable identifiers:
1. Prefer `id` or `data-testid` attributes (e.g., `#username`, `[data-testid="submit-btn"]`).
2. Avoid auto-generated or dynamic CSS class names (e.g., `.Button__sc-12345-0`).
3. Ensure selectors uniquely identify the target inputs in the DOM.

### Three User Flow Modes Explained
Lighthouse User Flows allow testing across three modes:
- **Navigation Mode (Cold Load)**: Audits a traditional page load, measuring all standard performance scores (like LCP and Speed Index). It performs a full refresh.
- **Timespan Mode (Interactions)**: Measures performance during user actions (e.g., scroll, click, modal popup). Focuses on Cumulative Layout Shift (CLS) and Total Blocking Time (TBT).
- **Snapshot Mode (Current State)**: Audits the page's current DOM structure at a specific moment in time (e.g., checking Accessibility score on an open modal dialog) without reloading the page.

### Common Gotchas & Troubleshooting
- **Two-Factor Authentication (2FA) & CAPTCHA**: Automated audits cannot bypass 2FA or CAPTCHAs. Use dedicated staging/testing environments where 2FA is disabled for test users, or use mock authentication cookies.
- **Session Expiry**: Lighthouse audits can take up to 2 minutes. If the backend has an aggressive session timeout (e.g., < 1 minute), the session may expire mid-audit. Ensure test environments have extended token expiry.
- **State Leakage**: Ensure the automated browser starts with clean storage (`--incognito` or fresh profiles) so cached data doesn't skew performance results.

### Cold vs. Warm Load Comparison

A **cold load** is the default Lighthouse behaviour: before each navigation it clears the browser cache, cookies, service worker registrations, and storage. This simulates a first-time visitor.

A **warm load** uses `disableStorageReset: true` in the navigation settings, which keeps the cache, service workers, and storage intact from the previous navigation. This simulates a returning visitor or an in-session page switch.

Why this matters:
- Cold load LCP is often 2–5× longer than warm load LCP because images, fonts, and scripts must be downloaded from the network.
- Warm loads reveal how well your caching strategy works (HTTP cache headers, service workers, font-display swap).
- CI pipelines should test **both** — cold to guard first-visit experience, warm to validate caching.

```javascript
// Cold navigation (default — clears everything)
await flow.navigate(url, { stepName: 'Cold Load' });

// Warm navigation (keeps cache and storage)
await flow.navigate(url, {
  stepName: 'Warm Load',
  configContext: { settings: { disableStorageReset: true } },
});
```

### When to Use Each Flow Mode

| Mode | API Call | What It Measures | Key Metrics | When to Use |
|---|---|---|---|---|
| **Navigation** | `flow.navigate(url)` | Full page load from start to fully interactive | LCP, FCP, SI, TBT, CLS, TTI | Testing page load performance (cold or warm) |
| **Snapshot** | `flow.snapshot()` | Current DOM state — no page load triggered | Accessibility, Best Practices, SEO | Auditing a modal, filled form, expanded panel, or any interactive state |
| **Timespan** | `flow.startTimespan()` ... `flow.endTimespan()` | Metrics during a window of user interactions | CLS, TBT, INP, Long Tasks | Measuring scroll jank, button responsiveness, layout shifts from lazy-load |

**Important**: Snapshot mode does NOT report Performance scores because there is no navigation event. If you need Performance scores for a page behind interactions, use Navigation mode after reaching the desired state.

### The Unified Flow Report

When you combine multiple modes in one `startFlow()` session, Lighthouse generates a **single unified HTML report** that shows every step in sequence:

```
┌─────────────────────────────────────────────┐
│ Flow Report: Checkout User Journey          │
│                                             │
│ Step 1: Cold Load (Navigation)      92 perf │
│ Step 2: Warm Load (Navigation)      98 perf │
│ Step 3: Form Filling (Timespan)     0.02 CLS│
│ Step 4: Payment Modal (Snapshot)    95 a11y  │
└─────────────────────────────────────────────┘
```

Generate the unified report with:
```javascript
const flowResult = await flow.createFlowResult(); // JSON (for assertions)
const htmlReport = await flow.generateReport();    // HTML (for humans)
```

The JSON structure contains a `steps` array where each step has a full `lhr` (Lighthouse Result) object, so you can programmatically extract scores per step.


