---
name: autonomous-e2e-testing
description: "Understand requirements, discover flows, generate E2E scenarios, write/execute Playwright and Robot Framework E2E suites for web and mobile, analyze failures, and improve test coverage."
---

# Autonomous End-to-End (E2E) Testing

## Purpose
End-to-End (E2E) testing validates complete user journeys and critical integration points across the entire system, ensuring that software updates do not disrupt core business operations. This skill enables the AI agent to autonomously understand requirements, discover user flows, generate E2E scenarios, and author/execute/maintain robust test suites in Playwright (Python) and Robot Framework (Python-based) for web and mobile applications.

---

## When to Use
Activate this skill when:
- Designing or writing automated E2E tests for web or mobile applications.
- Automating happy path user journeys (e.g., login → purchase → checkout).
- Setting up cross-browser test configurations or running tests in multiple browser engines.
- Implementing authentication flows (session preservation, API-based bypass, login automation).
- Testing role-based access control (RBAC) across multiple user permissions.
- Creating basic performance smoke checks (verifying action/load latency remains within SLAs).
- Autonomously executing tests, analyzing failures, and generating reports/recommendations.

## When NOT to Use
Do NOT activate this skill when:
- Testing unit-level edge cases or isolated helper functions (write unit tests instead).
- Testing every permutation of form validation (e.g., character boundaries, format strings) which are better suited for unit/component tests.
- Verifying internal implementation details (e.g., private class methods or database states).
- Generating Gherkin-style BDD tests for Selenium Python from user stories (use `test-case-generator` instead).
- Verifying REST API responses against OpenAPI/Swagger specifications (use `api-contract-tester` instead).
- Troubleshooting flaky tests, locator compliance, or configuring self-healing runs (use `flaky-test-and-self-healing` instead).
- Creating short, fast-running (< 5 mins) post-deployment sanity suites (use `smoke-test-builder` instead).

---

## Prerequisites
Before running the E2E tests, ensure the required packages and dependencies are installed:
- **Playwright Python**:
  ```bash
  pip install playwright pytest pytest-playwright pytest-xdist
  playwright install chromium firefox webkit
  ```
- **Robot Framework**:
  ```bash
  pip install robotframework robotframework-seleniumlibrary robotframework-appiumlibrary robotframework-requests pabot
  ```
- **Appium Mobile Testing**:
  Ensure Appium server is running locally or accessible on a remote grid.
  ```bash
  pip install Appium-Python-Client
  ```

---

## Process

Follow these 8 steps to manage the autonomous E2E testing lifecycle:

1. **Understand Requirements & User Stories**: Parse application requirements, user stories, and acceptance criteria to map out critical user flows.
2. **Discover Application Flows**: Map the application's entry points, page transitions, and transactional routes (e.g., Login, Dashboard, Cart, Checkout).
3. **Generate E2E Test Scenarios**: Outline high-level, happy-path test scenarios. Define expected behavior, inputs, and integration assertions.
4. **Create & Maintain Test Automation Code**: Generate or update clean, modular E2E test scripts utilizing page objects, robust locators, and dynamic waits.
5. **Execute Tests Autonomously**: Run the generated test suites using automated execution commands (e.g., `pytest` or `robot`) in target environments.
6. **Analyze Failures**: If a test fails, capture and parse error logs, console warnings, and page screenshots to diagnose root causes (e.g., code regression, selector mismatch, network error). Use the analysis tool [analyze-e2e-results.py](file:///c:/Users/costrategix/.gemini/antigravity-ide/brain/SkillCreatorPOC/.agents/skills/autonomous-e2e-testing/scripts/analyze-e2e-results.py) to parse result files.
7. **Generate Reports & Recommendations**: Summarize execution results, identify critical system issues, and recommend code or test suite fixes.
8. **Continuously Improve Test Coverage**: Identify gaps in the E2E flow (e.g., untested RBAC roles, missing browsers) and extend the test suite.

---

## Decision Rules and Conditional Logic

- **IF** testing a **Web Application** **THEN** use **Playwright Python** by default, structuring scripts with Page Objects. Use **Robot Framework** (SeleniumLibrary) if requested by the user.
- **IF** testing a **Mobile Application** **THEN** use **Appium Python** or **Robot Framework** (AppiumLibrary). Define Desired Capabilities (platformName, deviceName, appPackage, appActivity) explicitly.
- **IF** the application has an **Authentication Flow** **THEN**:
  - Bypass repeated UI logins by saving and loading session cookies or tokens (e.g., using Playwright's `storage_state` or Robot's request cookies).
  - Use API-based authentication seeding to generate access tokens and inject them directly into browser storage.
- **IF** testing **Role-Based Access Control (RBAC)** **THEN** define a matrix of user roles (e.g., Admin, Editor, Viewer) and test that permissions restrict page access and actions correctly.
- **IF** **Cross-Browser Compatibility** is required **THEN** configure Playwright to run across `chromium`, `firefox`, and `webkit` in parallel.
- **IF** **Performance Smoke Checks** are requested **THEN** measure the time elapsed from navigation start to load event or the execution duration of critical actions (e.g., payment submission) and assert it is under SLA bounds (e.g., < 3 seconds).

---

## Target Platforms and File Specifications
This skill operates on Python source files (`.py`) and Robot Framework test files (`.robot`). It uses the following command line tools:
- `pytest`: Used to execute Playwright-Python suites.
- `robot`: Used to execute Robot Framework suites.
- `pabot`: Used to execute Robot Framework suites in parallel processes.
- `appium`: Used for mobile automation driver hosting.

Refer to the E2E best practices guide in [e2e-best-practices.md](file:///c:/Users/costrategix/.gemini/antigravity-ide/brain/SkillCreatorPOC/.agents/skills/autonomous-e2e-testing/references/e2e-best-practices.md) for more details.

---

## Recommended Tools and Commands

- Run Playwright E2E tests in parallel:
  ```bash
  pytest --numprocesses auto --browser chromium --browser firefox --browser webkit
  ```
- Run Robot Framework tests in parallel:
  ```bash
  pabot --processes 4 --outputdir results/ my_suite.robot
  ```
- Debug a Playwright test with UI trace:
  ```bash
  pytest --headed --slowmo 500
  ```

---

## Output Format
All generated E2E testing artifacts must be organized as follows:

### 1. E2E Test Strategy & Flow Map
Include a summary of the application flows, user roles, browsers/devices, and integration points.

### 2. High-Level Scenarios (Given/When/Then)
Define the scenarios focusing on critical business paths.

### 3. Automation Scripts
Provide complete, functional code blocks with Page Object imports, parameterized configurations, and explicit assertions.

### 4. Verification & Execution Instructions
Explain how to configure environment variables, run the scripts, and review reports.

---

## Examples

### Example 1: Web Purchase Journey in Playwright Python (with session state & performance check)
This script demonstrates login bypass via state recovery, a happy-path purchase flow, and a performance SLA check.

```python
# filepath: tests/test_purchase.py
import pytest
import time
from playwright.sync_api import Page, expect

# Setup configuration to load saved session state
@pytest.fixture(scope="function")
def context_args(browser_context_args):
    return {
        **browser_context_args,
        "storage_state": "auth/customer_state.json"
    }

def test_happy_path_purchase(page: Page):
    # Performance check: start timer
    start_time = time.time()
    
    # 1. Navigate to dashboard (session state handles login automatically)
    page.goto("https://app.example.com/dashboard")
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible()
    
    # 2. Select product
    page.get_by_role("link", name="Products").click()
    page.get_by_role("button", name="Add Pro Plan").click()
    
    # 3. Checkout and Payment Submission
    page.get_by_role("link", name="Cart").click()
    page.get_by_role("button", name="Proceed to Checkout").click()
    
    page.get_by_label("Card Number").fill("4242424242424242")
    page.get_by_label("Expiry Date").fill("12/28")
    page.get_by_label("CVC").fill("123")
    
    page.get_by_role("button", name="Submit Payment").click()
    
    # 4. Assert success confirmation
    expect(page.get_by_role("heading", name="Thank you for your purchase!")).to_be_visible()
    
    # Performance assertion: verify total journey took under 4 seconds
    duration = time.time() - start_time
    assert duration < 4.0, f"Purchase journey exceeded SLA: took {duration:.2f}s"
```

### Example 2: Mobile Hotel Booking in Robot Framework (AppiumLibrary)
This example shows a structured mobile E2E happy-path user journey using custom keyword abstractions.

```robot
# filepath: tests/mobile_booking.robot
*** Settings ***
Library          AppiumLibrary
Suite Setup      Open Booking Application
Suite Teardown   Close All Applications

*** Variables ***
${REMOTE_URL}           http://localhost:4723/wd/hub
${PLATFORM_NAME}        Android
${DEVICE_NAME}          emulator-5554
${APP_PACKAGE}          com.example.hotelbooking
${APP_ACTIVITY}         com.example.hotelbooking.MainActivity

*** Test Cases ***
Successful Hotel Booking Journey
    Given User Starts On Splash Screen
    When User Searches For Hotel In City    New York
    And User Selects First Available Hotel
    And User Confirms Booking With Guest Details    John Doe    john.doe@example.com
    Then Booking Success Screen Should Be Displayed

*** Keywords ***
Open Booking Application
    Open Application    ${REMOTE_URL}
    ...    platformName=${PLATFORM_NAME}
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    automationName=UiAutomator2

User Starts On Splash Screen
    Wait Until Element Is Visible    id=com.example.hotelbooking:id/btn_get_started    15s
    Click Element    id=com.example.hotelbooking:id/btn_get_started

User Searches For Hotel In City
    [Arguments]    ${city}
    Wait Until Element Is Visible    id=com.example.hotelbooking:id/search_bar    10s
    Input Text    id=com.example.hotelbooking:id/search_bar    ${city}
    Click Element    id=com.example.hotelbooking:id/btn_search

User Selects First Available Hotel
    Wait Until Element Is Visible    id=com.example.hotelbooking:id/hotel_list_item    10s
    Click Element    xpath=(//android.widget.RelativeLayout[@resource-id="com.example.hotelbooking:id/hotel_list_item"])[1]
    Wait Until Element Is Visible    id=com.example.hotelbooking:id/btn_book_now    10s
    Click Element    id=com.example.hotelbooking:id/btn_book_now

User Confirms Booking With Guest Details
    [Arguments]    ${name}    ${email}
    Wait Until Element Is Visible    id=com.example.hotelbooking:id/input_name    10s
    Input Text    id=com.example.hotelbooking:id/input_name    ${name}
    Input Text    id=com.example.hotelbooking:id/input_email    ${email}
    Click Element    id=com.example.hotelbooking:id/btn_confirm_booking

Booking Success Screen Should Be Displayed
    Wait Until Element Is Visible    id=com.example.hotelbooking:id/txt_booking_success    15s
    Element Text Should Be    id=com.example.hotelbooking:id/txt_booking_success    Booking Confirmed!
```

---

## Pitfalls & Anti-Patterns to Avoid

- **Over-testing Form Field Validation**: Waste of execution time writing complex UI scenarios for trivial form validation boundaries (like field character limit, valid emails) that are more rapidly tested at the unit level.
- **No Parallel Execution**: Running E2E suites sequentially, which slows down the feed loop. Always utilize tools like `pytest-xdist` or `pabot` to scale.
- **Ignoring Data Cleanup**: Leaving leftover items and users in database tables, leading to naming conflicts and test dependencies.
- **Static Sleeps**: Inserting hardcoded sleep pauses like `time.sleep(10)` to wait for server response, instead of dynamic waits.

---

## Changelog & Version History

### [1.0.0] - 2026-06-22
- **Initial Release**: Launched the `autonomous-e2e-testing` skill directory.
- **Cross-Framework Support**: Configured instructions for both Playwright-Python and Robot Framework.
- **Mobile Capabilities**: Included Appium guidelines and desired configurations.
- **Reference & Script Tools**: Added [e2e-best-practices.md](file:///c:/Users/costrategix/.gemini/antigravity-ide/brain/SkillCreatorPOC/.agents/skills/autonomous-e2e-testing/references/e2e-best-practices.md) and [analyze-e2e-results.py](file:///c:/Users/costrategix/.gemini/antigravity-ide/brain/SkillCreatorPOC/.agents/skills/autonomous-e2e-testing/scripts/analyze-e2e-results.py).

