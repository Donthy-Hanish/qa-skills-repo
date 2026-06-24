# E2E Testing Best Practices

Follow these industry-standard best practices to ensure that your automated E2E tests are stable, fast, and maintainable.

## 1. Test Isolation & Clean State
- **Rule**: Every test must run independently from others. Never chain tests where Test B depends on the outcome or state of Test A.
- **Action**: Always reset browser cookies/context or mobile application state (e.g., app data) before each test run. Use pytest fixtures or Robot setup/teardown keywords to clear and prepare the workspace.

## 2. Fast Authentication (Bypass Login UI)
- **Rule**: Avoid going through the login page UI for every single test scenario. This introduces huge timing overhead and increases points of failure.
- **Action**:
  - Perform login once, extract the authentication cookies or sessionStorage tokens, and reuse them for subsequent tests.
  - In Playwright, utilize the `storage_state` option:
    ```python
    # Save state
    context.storage_state(path="auth/state.json")
    # Load state
    context = browser.new_context(storage_state="auth/state.json")
    ```
  - In API/Web integrations, hit the login endpoint directly via HTTP POST, retrieve the token, and inject it into the browser context.

## 3. Selector Strategy (Accessibility-First)
- **Rule**: Avoid using absolute XPaths (`/html/body/div[2]/form/input`) or raw CSS classes (`.btn-primary-active`) that are highly prone to breakdown when layout or styling changes.
- **Action**:
  - Prefer explicit test IDs (e.g., `data-testid="submit-payment"`).
  - Use accessible names and roles (e.g., `page.get_by_role("button", name="Submit")`).
  - Rely on stable visible text (e.g., `page.get_by_text("Order Confirmed")`).

## 4. Avoid Hardcoded Delays (No Static Sleep)
- **Rule**: Hardcoded pauses (e.g., `time.sleep(5)` or `Sleep 5s`) cause slow executions and flaky failures under heavy network loads.
- **Action**: Use dynamic polling assertions that wait for the element or state to exist before interacting:
  - Playwright: `expect(locator).to_be_visible(timeout=5000)`
  - Robot Framework: `Wait Until Element Is Visible    locator    timeout=5s`

## 5. Dynamic Test Data & Cleanup
- **Rule**: Hardcoded resource names or accounts will conflict when tests run in parallel, causing false positives/negatives.
- **Action**:
  - Append random numbers or timestamps to usernames, email addresses, and purchase item names.
  - Implement a teardown step to delete generated test resources via API calls or database scripts.