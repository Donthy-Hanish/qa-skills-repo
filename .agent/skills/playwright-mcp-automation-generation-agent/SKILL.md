---
name: playwright-mcp-automation-generation-agent
description: "Generate a complete Playwright Python framework with POMs, tests, and fixtures. Trigger when asked to generate automated tests, write automation code, or create Page Object Models."
---

# Playwright MCP Automation Generation Agent

## Purpose
To build a highly modular, maintainable Playwright Python test automation framework based on test plans, adhering strictly to the Test Locator Standard for stability.

## When to Use
Activate this skill when:
- Asked to generate automated test scripts or a full Playwright Python framework from a test plan.
- Building Page Object Models (POMs), fixtures, or utility helpers for a web application.
- Writing automation code following the Test Locator Standard (data-testid, aria-label, roles).
- Generating smoke, regression, critical path, or defect validation test suites.

## Process
1. Consume inputs:
   - `specs/test-plan.md`
   - `specs/exploratory-findings.md`
2. Apply the **Test Locator Standard V1.0** locator selection priority when generating elements:
   - **Priority 1**: `data-testid` / `data-qa` / `automation-id`
     - Use lowercase `kebab-case` naming convention (e.g., `data-testid="submit-order"`).
     - Must represent business meaning, not UI visual style (do NOT use `data-testid="blue-button"`).
   - **Priority 2**: `aria-label`
   - **Priority 3**: `role` + accessible name (e.g. `page.get_by_role("button", name="Log in")`)
   - **Priority 4**: Stable visible text
   - **Priority 5**: CSS selectors (stable only)
   - **Priority 6**: Relative XPath (last resort)
   - **Priority 7**: Absolute XPath (**NEVER ALLOWED**, e.g., `xpath=//div[3]/span/button`)
   - Avoid auto-generated IDs, dynamic class names, and index-based XPath.
3. Structure the generated Python framework:
   ```
   project-root/
   ├── tests/
   │   └── *.spec.py (Automated tests for Smoke, Regression, Critical Path, High Priority, and Defect Validation)
   ├── pages/
   │   └── *.py (Page Object Models)
   ├── fixtures/
   │   └── *.py (Playwright fixtures)
   ├── test-data/
   ├── utils/
   │   └── *.py (Utilities for smart waits, retries)
   ├── reports/
   ├── screenshots/
   └── playwright.config.py
   ```
4. Write reusable code utilizing explicit assertions, smart waits, retry logic, and cross-browser configurations.

## Output Format
Generation of clean python code files in `tests/`, `pages/`, `fixtures/`, and config files at the root matching the standard POM structure.

## Examples
### Example 1: Page Object using Standard Locators
**File: pages/login_page.py**
```python
class LoginPage:
    def __init__(self, page):
        self.page = page
        # Priority 1: Stable data-testid selector
        self.username_input = page.locator('css=[data-testid="username-input"]')
        self.password_input = page.locator('css=[data-testid="password-input"]')
        # Priority 3: Role selector
        self.login_button = page.get_by_role("button", name="Login")

    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
```

## Edge Cases
- **Dynamic Elements without IDs**: Fallback to Priority 3 (`role` + accessible name) or Priority 4 (visible text). Never write absolute xpath!
- **Kendo or React dynamic popups**: Use smart waits to ensure overlay elements load before click actions.
