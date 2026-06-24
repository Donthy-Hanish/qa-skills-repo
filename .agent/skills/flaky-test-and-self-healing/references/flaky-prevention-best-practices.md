# Flaky Test Prevention & Automation Best Practices

While self-healing repairs tests at runtime, **preventing flakiness** requires structural changes to how automated tests are written. This reference guide outlines the team conventions for Test Isolation, Data Independence, Deterministic Validation, and Over-Healing Prevention.

---

## 1. Test Isolation Principles

Tests should be modular and fully isolated. A test suite must never depend on the outcome of a prior test, nor should tests assume a particular execution sequence.

### Conventions:
- **Fresh Context per Test**: Reset the browser cache, cookies, and context in the setup. In Robot Framework, utilize `Close All Browsers` in suite teardowns and launch fresh instances in suite setups.
- **Independent State Initialization**: Do not navigate through 5 pages of the UI to set up preconditions for a test case. 
  - *Recommendation*: Use backend REST API calls inside your Setup keywords (e.g., using `RequestsLibrary`) to create accounts or seed test data, then navigate directly to the page under test.
- **Teardown Cleanliness**: Always ensure a test cleans up after itself. If a test fails halfway, the `Teardown` keyword must still execute to release locked accounts, close modals, or delete created entities.

```robot
*** Keywords ***
Setup Test Environment
    [Documentation]    Creates a user via API and logs them in before testing
    ${user_credentials}=    Create Test User Via API
    Open Browser To Page    ${LOGIN_URL}
    Submit Credentials    ${user_credentials}
```

---

## 2. Data Independence Standards

Dynamic, concurrent test runs will collide if tests rely on shared static data (like a fixed username `testuser@company.com` or static account IDs).

### Conventions:
- **Dynamic Payloads**: Always append random strings or Unix timestamps to generated emails, names, or reference codes.
  ```robot
  *** Keywords ***
  Generate Unique Email
      ${random_string}=    Generate Random String    8    [LOWER]
      ${email}=    Set Variable    user-${random_string}@stage.com
      [Return]    ${email}
  ```
- **Concurrency Isolation**: If running parallel tests using tools like `pabot`, ensure that different test threads target unique sub-tenants or separate testing sandbox IDs.
- **No Shared Database Assertions**: Do not assert the exact count of list items (e.g., asserting there are exactly 12 freelancers in the database) since concurrent threads might add/delete records dynamically. Assert relative correctness instead.

---

## 3. Deterministic Validation & Timing

Timing is the single greatest driver of CI flakiness. The use of hardcoded static waits (`Sleep 5s`) is highly discouraged.

### Conventions:
- **Poll for Elements**: Replace static `Sleep` statements with polling loops that wait for elements to reach a specific state (visible, clickable, enabled).
- **Stale Element Handling**: Modern React/Kendo platforms refresh elements during background re-renders. Standardize keywords to automatically catch stale elements and attempt to re-locate them.
- **Wait for Network Silence**: Wait for loading spinners or progress bars to disappear before asserting UI changes.

*Before (Flaky):*
```robot
# Dynamic list loading takes variable time on CI
Click Element    id=submit-btn
Sleep            3s
Element Should Be Visible    id=success-msg
```

*After (Deterministic):*
```robot
# Safe and immediate execution
Smart Click    css=[data-testid="submit-btn"]
Smart Wait For Element    css=[data-testid="success-msg"]    timeout=10s
```

---

## 4. Avoiding Over-Healing

Self-healing is designed to fix *locator structural modifications* or *temporary timing lags*. It must **never** be used to mask true application regressions or functional bugs.

```
       +---------------------------------------------+
       | Does Locator Standard priority scan match?  |
       +---------------------------------------------+
                              |
                     [Candidate Found?]
                              |
               +--------------+--------------+
               |                             |
             [YES]                          [NO]
               |                             |
       [Is Element Disabled?]         [Fail Test Case]
               |
         +-----+-----+
         |           |
       [YES]        [NO]
         |           |
 [FAIL FAST: Bug!] [Heal Locator & Click]
```

### Safety Boundaries:
1. **Disabled and Read-Only Components**: If the primary element is found but is disabled (e.g., a "Submit" button is greyed out because of incomplete form validations), the framework **must fail immediately**. Do NOT search for other buttons or attempt to force interaction.
2. **Page Errors & Validation Banners**: If a form submission triggers a "400 Bad Request" or "Validation Error" banner, this is a functional failure. Do NOT try to heal locators to bypass the validation error.
3. **Always Log and Alert**: The self-healing engine must never operate silently. An automated test that passes via self-healing is still considered a **warning** and must write a locator update recommendation to the diagnostic report.
4. **Assert Business Logic**: Ensure tests have explicit business logic assertions at the end (e.g. asserting that a database record was updated or a distinct success message is displayed). Self-healing cannot fix broken logic!
