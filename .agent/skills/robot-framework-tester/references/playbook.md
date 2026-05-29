# Robot Framework QA Playbook

This playbook serves as a comprehensive guide for implementing and executing automated tests using Robot Framework, SeleniumLibrary, RequestsLibrary, and JSONLibrary.

---

## 1. Dependency Setup

To ensure reproducible test runs across local environments and CI/CD pipelines, always pin dependencies in your `requirements.txt`. Below is the standard dependency set:

```txt
robotframework==6.1.1
robotframework-seleniumlibrary==6.1.3
robotframework-requests==0.9.5
robotframework-jsonlibrary==0.5
pabot==2.16.0
```

### Installation
Run the following command to install the pinned dependencies:
```bash
pip install -r requirements.txt
```

---

## 2. Local Execution Commands

Execute tests using either the standard `robot` runner or `pabot` for concurrent execution.

### Run Full Suite
Saves all reports, logs, and screenshots in the `results/` directory:
```bash
robot --outputdir results tests/
```

### Run by Tag
Run only tests tagged with `smoke` or `regression`:
```bash
robot --include smoke tests/
robot --include smokeORregression tests/
```

### Exclude Tags
Exclude work-in-progress (WIP) or flaky tests:
```bash
robot --exclude wip tests/
```

### Parallel Execution (Pabot)
Run tests concurrently across 4 worker processes to reduce execution time:
```bash
pabot --processes 4 tests/
```

---

## 3. Internal Selenium Grid Setup

When running tests against an internal Selenium Grid rather than a local browser, configure `SeleniumLibrary` to run remotely using the `options` parameter.

> [!NOTE]
> The `desired_capabilities` parameter was deprecated in SeleniumLibrary 6.x. Always configure browser settings using the modern `options` parameter instead of `desired_capabilities`.

### Grid URL
```txt
remote_url=http://selenium-grid:4444/wd/hub
```

### Configuration Example
```robot
*** Settings ***
Library           SeleniumLibrary

*** Variables ***
${GRID_URL}       http://selenium-grid:4444/wd/hub
${BROWSER}        chrome

*** Keywords ***
Open Remote Chrome Browser
    [Arguments]    ${target_url}
    Open Browser    ${target_url}    browser=${BROWSER}    remote_url=${GRID_URL}    options=add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")

Open Remote Firefox Browser
    [Arguments]    ${target_url}
    Open Browser    ${target_url}    browser=firefox    remote_url=${GRID_URL}    options=add_argument("--headless");add_argument("--no-sandbox")
```

---

## 4. Debugging Common Errors

| # | Error Message / Exception | Probable Cause | Fix / Solution |
|---|---------------------------|----------------|----------------|
| 1 | `ElementNotFound` / `Element with locator '...' not found` | The element is not present in the DOM, or the locator has changed, or the page hasn't loaded yet. | 1. Ensure a dynamic wait like `Wait Until Element Is Visible` is called before acting.<br>2. Check for iframe contexts; switch if necessary (`Select Frame`).<br>3. Verify locator accuracy in the browser dev tools. |
| 2 | `StaleElementReferenceException` | The page updated or re-rendered, and the reference to the element is no longer valid. | 1. Re-locate the element by waiting again.<br>2. Use `Wait Until Keyword Succeeds` to retry the action. |
| 3 | `TimeoutException` | The element did not appear, disappear, or become enabled within the specified timeout. | 1. Increase the default timeout if the page is slow.<br>2. Check if there was an underlying system/network error.<br>3. Verify the conditions (e.g. element hidden vs not present). |
| 4 | `SessionNotCreatedException` | ChromeDriver (or geckodriver) version is incompatible with the installed browser version. | 1. Update webdrivers using webdriver-manager.<br>2. Pin or match the browser and driver versions in the execution environment. |
| 5 | `WebDriverException: Message: Service ... executable needs to be in PATH` | Webdriver executable is missing from the environment PATH variable. | 1. Add the path to chromedriver/geckodriver to the system environment PATH.<br>2. Use a webdriver manager library to handle installations automatically. |
| 6 | `ConnectionError` (from RequestsLibrary) | The target REST API endpoint is unreachable or the server is down. | 1. Check if the base URL is correct.<br>2. Verify network configuration, VPNs, or firewalls.<br>3. Add a ping or health check step before running API tests. |
| 7 | `JSONDecodeError: Expecting value: line 1 column 1` | The API returned a non-JSON response (e.g., HTML error page, plain text, or empty body) when JSON was expected. | 1. Log the response content using `Log To Console  ${response.content}` to inspect the error.<br>2. Add status code assertions to fail early if an error page is returned. |
| 8 | `HTTPError` / Status code mismatch | The API returned a failure code (e.g. 500, 404, 400) instead of the expected success code (e.g. 200). | 1. Inspect request payload and headers for correct format.<br>2. Ensure required auth tokens are active and valid. |
| 9 | `No keyword with name '...' found` | The keyword name is misspelled, or the library/resource defining it is not imported under `*** Settings ***`. | 1. Double check the spelling of the keyword.<br>2. Ensure the correct `Library` or `Resource` file is imported.<br>3. Check relative pathing in `Resource` imports. |
| 10| `Variable '...' not found` | The variable was not declared, or is accessed outside its scope (e.g., test scope vs suite scope), or misspelled. | 1. Declare the variable in the `*** Variables ***` section or using `Set Suite Variable` / `Set Test Variable`.<br>2. Check spelling and case sensitivity. |
| 11| `KeyError` (Collections/JSONLibrary) | Attempting to access a dictionary key or JSON path that does not exist in the response. | 1. Log the dictionary/JSON structure before retrieving.<br>2. Use `Run Keyword And Return Status` to check key existence before accessing. |
| 12| `Setup failed: ...` or `Teardown failed: ...` | Preconditions failed (e.g. database down, login failed) or teardown encountered an error (e.g. browser already closed). | 1. Wrap teardown keyword calls in `Run Keyword And Ignore Error` where appropriate (e.g., closing connections).<br>2. Ensure dependencies in Setup are fully active. |
| 13| `Multiple keywords with name '...' found` | Two imported resource files or libraries define keywords with the exact same name. | 1. Prefix the keyword with the resource/library name (e.g., `SeleniumLibrary.Click Element` or `MyCustomResource.Login`). |

---

## 5. Best Practices Checklist

- [ ] **1. Never Use Hardcoded Sleeps:** Use dynamic waits like `Wait Until Element Is Visible` or `Wait Until Element Is Enabled`.
- [ ] **2. Robust Selectors:** Prioritize stable identifiers (`id`, `name`, `data-testid`). Avoid long, absolute XPaths.
- [ ] **3. Page Object Pattern:** Structure UI interactions using `.resource` Page Objects. Keep locators and keywords encapsulated.
- [ ] **4. Clean Test Cases:** Keep `.robot` test cases declarative and focused on the business flow. Move technical details to Resource files.
- [ ] **5. Suite-Level Lifecycle:** Use `Suite Setup` and `Suite Teardown` for browser lifecycle management rather than starting/stopping browsers in individual tests.
- [ ] **6. Strict Teardown Execution:** Always ensure `Suite Teardown` runs (e.g., `Close All Browsers`) even if tests fail.
- [ ] **7. Logical Tagging:** Tag tests logically (`smoke`, `regression`, `critical`, `slow`).
- [ ] **8. Descriptive Documentation:** Add clear `Documentation` fields to all suites, test cases, and complex keywords.
- [ ] **9. Variable Scoping:** Use descriptive uppercase names for global/suite variables (`${BASE_URL}`) and lowercase/camelCase for local keyword variables (`${username}`).
- [ ] **10. Extract Complex Logic:** Avoid writing Python-like loops/conditions inside `.robot` files. Extract complex data manipulation into Python helper scripts (`.py`).
- [ ] **11. Clean Formatting:** Use standard indentation (4 spaces) and avoid mixing tabs and spaces.
- [ ] **12. Error Logging:** Log API payloads and response bodies on failure using `Log` or `Log To Console` to simplify troubleshooting.
- [ ] **13. API Session Reuse:** Use `Create Session` once in suite setup and reuse the session across all API tests to reduce overhead.
- [ ] **14. Pin Dependencies:** Ensure the same versions of libraries are used in all development and execution environments.

---

## 6. Report Analysis

Robot Framework generates three primary output files after every run:

### 1. `output.xml`
- **What it is:** Machine-readable XML file containing all execution details, logs, timings, and status of every keyword.
- **How to use it:** This is the source-of-truth file. It is used by CI/CD tools (like Jenkins, GitLab CI) to display test status graphs, and by report mergers (`rebot`) to combine multiple test runs.

### 2. `log.html`
- **What it is:** A highly detailed HTML document showing the hierarchical execution tree of every test case, down to individual keywords and arguments.
- **How to use it:** The primary tool for debugging. When a test fails:
  1. Open `log.html` in a browser.
  2. Locate the failed test case (highlighted in red).
  3. Expand the nested keywords to see the exact step that failed.
  4. View captured screenshots (automatically embedded by `SeleniumLibrary` on failure).

### 3. `report.html`
- **What it is:** A high-level dashboard showing statistics (passed, failed, elapsed time) categorized by suite and tag.
- **How to use it:** Use this for executive summaries or checking the health of a test run at a glance.
