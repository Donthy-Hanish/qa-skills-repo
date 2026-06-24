---
name: flaky-test-and-self-healing
description: "Detect flaky UI/API tests, auto-heal locator or timing failures, and audit locator compliance. Trigger on detect flaky tests, self-healing, fix flaky UI tests, or stabilize robot tests."
---

## What This Skill Does

This skill provides a complete runtime and analysis framework to **detect flaky tests, isolate instability patterns, and auto-heal locator or timing failures** in UI and API test suites. 

It is built specifically for **Robot Framework with Python** and consists of two primary components:
1. **`SelfHealingLibrary.py` (Runtime Component)**: A custom Robot Framework companion library that intercepts element interactions (clicks, text input, waits) and auto-heals broken locators in real-time. It uses an accessibility-first priority fallback search fully compliant with the [Test Locator Standard](file:///C:/Users/costrategix/.gemini/antigravity-ide/brain/SkillCreatorPOC/Reference/Test%20Locator%20Standard.pdf) and writes healing recommendations to `./self_healing_report.json` instead of silently over-healing.
2. **`analyze_flakiness.py` (Analysis Component)**: A command-line utility that compares multiple execution runs (using `output.xml` logs) to isolate flaky tests, perform Root Cause Analysis (RCA) on exceptions, and audit locators for compliance with standard styling (e.g. flags dynamic IDs, absolute XPaths, and index-based selectors).

---

## When to Use

### Activate this skill when the user:
- Asks to detect, analyze, or prevent flaky tests in Robot Framework suites.
- Wants to implement runtime self-healing locators or dynamic waiting mechanisms.
- Needs to parse and audit `output.xml` logs across multiple test executions.
- Is troubleshooting element synchronization failures, `StaleElementReferenceException`, `NoSuchElementException`, or `TimeoutException`.
- Wants to audit Robot resource files and test cases against the **Test Locator Standard**.
- Asks for guidelines on test isolation, data independence, or removing static `Sleep` statements.

### Do NOT activate this skill when the user:
- Wants to generate new functional BDD/Gherkin test cases from a user story (use `test-case-generator` instead).
- Wants to run OpenAPI/Swagger contract tests for REST APIs (use `api-contract-tester` instead).
- Is debugging simple local installation issues of python or pip that do not involve test suites.
- Needs general unit test creation (e.g. using `unittest` or `pytest`) unrelated to end-to-end web/API automation.

---

## Core Principles

To ensure automation stability and maintainability, always enforce these principles:
- **Accessibility-First Locators**: Prioritize locators in this exact order:
  1. Custom test attributes: `css=[data-testid="..."]`, `css=[data-qa="..."]`, `css=[automation-id="..."]`
  2. `aria-label`
  3. `role` + accessible name
  4. Stable visible text
  5. Stable CSS selectors
  6. Relative XPath (last resort, e.g. `xpath=//button[@id="submit"]`)
  - *Never* use absolute XPath (`xpath=//div[2]/span/button`) or index-based selectors.
- **Strict Bounds on Self-Healing (No Over-Healing)**: Only heal locator structural mismatch or timing issues. **Never** bypass functional bugs (e.g., mismatched text values, page-level HTTP 500 errors, or disabled components that prevent submission).
- **Test Isolation & Data Independence**: Each test must manage its own state. Use random/unique suffixes for created records and reset browser contexts between tests to prevent cascading flakiness.
- **Deterministic Validation**: Always poll for target states rather than using hardcoded delays (e.g. `Sleep 5s` is prohibited; use `Smart Wait For Element` or `Wait Until Element Is Visible` instead).

---

## Decision Rules and Conditional Logic

Apply the following conditional rules when diagnosing and implementing self-healing:
- **IF** the primary locator fails due to a DOM change **THEN** trigger the accessibility-first fallback scanner to search for matches based on aria attributes, text, or historical map and log the suggestion.
- **IF** the target element is found but is disabled or read-only **THEN** fail immediately; do NOT attempt to click or heal, as this represents a functional logic flow or application bug.
- **IF** a `StaleElementReferenceException` occurs during interaction **THEN** immediately refresh the element reference by re-finding it up to 3 times before failing or healing.
- **IF** multiple runs of a test suite are provided (e.g., two or more `output.xml` files) **THEN** execute the flakiness comparison to isolate inconsistent test statuses (Pass -> Fail or Fail -> Pass) and highlight timing variance.

---

## Step-by-Step Process for QA Engineers & AI Agents

Follow these steps to deploy and utilize the flaky test and self-healing framework:

### Step 1: Install and Configure SelfHealingLibrary

1. Copy the `SelfHealingLibrary.py` from this skill's script directory to your project's libraries folder.
2. Import the library in your Robot Framework `.robot` resource files:
   ```robot
   *** Settings ***
   Library    SeleniumLibrary
   Library    path/to/SelfHealingLibrary.py    WITH NAME    SelfHealer
   ```
3. Initialize the library in your Suite Setup, passing the active instance of SeleniumLibrary:
   ```robot
   *** Keywords ***
   Initialize Custom Healing
       ${selenium_lib}=    Get Library Instance    SeleniumLibrary
       SelfHealer.Register Selenium Instance    ${selenium_lib}
   ```

### Step 2: Implement Resilient Interactivity Keywords

Replace standard interaction keywords with smart, self-healing equivalents:
- Replace `Click Element` with `Smart Click`
- Replace `Input Text` with `Smart Input Text`
- Replace `Wait Until Element Is Visible` with `Smart Wait For Element`

*Example Robot Test:*
```robot
*** Test Cases ***
Resilient User Checkout Flow
    [Setup]    Initialize Custom Healing
    Go To    ${BASE_URL}/checkout
    Smart Input Text    css=[data-testid="promo-input"]    DISCOUNT20
    Smart Click    css=[data-testid="apply-promo-btn"]
    Smart Wait For Element    css=[data-testid="promo-success-banner"]    timeout=10s
```

### Step 3: Analyze Test Flakiness & Locator Compliance

Execute `analyze_flakiness.py` post-run to parse your execution logs and audit code compliance:

```bash
# Compare runs to find flaky tests and trace exceptions
python path/to/analyze_flakiness.py --runs path/to/run1/output.xml path/to/run2/output.xml --output flakiness_report.md

# Audit local Robot test files for locator standard compliance
python path/to/analyze_flakiness.py --audit ./tests/ --output compliance_report.md
```

---

## Output Format

The `analyze_flakiness.py` CLI generates a detailed Markdown report. The expected structure of this output is:

```markdown
# Flaky Test & Compliance Analysis Report

## 1. Executive Summary
- **Total Tests Analyzed**: [Count]
- **Flaky Tests Detected**: [Count] ([%])
- **Compliance Score**: [Score]/100
- **Primary Flakiness Driver**: [Timing / Locator / Data / Network]

## 2. Flaky Test Summary
| Test Case Name | Run 1 Status | Run 2 Status | Root Cause Category | Key Exception / Traceback |
| :--- | :--- | :--- | :--- | :--- |
| `User Checkout` | FAIL | PASS | Timing Flake | `TimeoutException: Element not visible after 5s` |

## 3. Root Cause Analysis (RCA) Details
### [Test Case Name]
- **Symptom**: [Description of discrepancy]
- **Diagnostic Details**:
  ```
  [Stack trace or error excerpt]
  ```
- **Recommended Remediation**:
  - [Actionable steps, e.g. replace Sleep with dynamic polling, or use Smart Wait]

## 4. Test Locator Compliance Audit
List of violations against the **Test Locator Standard.pdf**:
- **Critical Violations (Absolute/Index XPath or Dynamic IDs)**:
  - `checkout.robot:L47`: `xpath=//div[3]/span/button` (Absolute XPath is forbidden)
  - `login.robot:L12`: `id=k-12345-email` (Dynamic framework ID detected)
- **Improvement Suggestions**:
  - `profile.robot:L89`: `css=.btn-blue` (Visual style class. Recommendation: Add data-testid="edit-profile-btn")

---
*Report generated by Flaky Test & Self-Healing Analyzer*
```

---

## Pitfalls & Anti-Patterns to Avoid

Keep these common pitfalls in mind when writing or executing self-healing tests:
- **Over-Healing True Regressions**: Do not allow the healing engine to bypass actual application bugs. If a submit button is disabled because a form validation failed, that is a bug or flow error; do not attempt to find other buttons or heal the click keyword.
- **Silent Healing (Hiding Automation Debt)**: Never run self-healing without generating a diagnostic report. If locators are healed silently, developers will never update the underlying source code, creating massive technical debt.
- **Relying on Dynamic Classes**: Avoid using dynamic or styling classes (like `.btn-blue`, `.Mui-focused`, or `.k-grid`) in locator healing. They change with visual updates, rendering the healing fragile.
- **Static Delay Crutches**: Do not fallback on `Sleep` calls to wait for pages to settle. Dynamic waits (e.g. `Smart Wait For Element`) should always be utilized instead.

---

## Changelog & Version History

### [1.0.0] - 2026-05-29
- **Initial Release**: Launched the `flaky-test-and-self-healing` skill.
- **Runtime Component**: Created `SelfHealingLibrary.py` for dynamic element lookup and stale retries.
- **Diagnostics CLI**: Implemented `analyze_flakiness.py` to compare output logs and audit locator conventions.
- **Knowledge Base**: Added design manuals for accessibility-first selectors and flakiness prevention.
