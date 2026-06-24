---
name: smoke-test-builder
description: "Generate post-deployment smoke test suites (scenarios, Playwright/Newman/Robot scripts, CI/CD config) under 5 mins. Trigger: 'generate smoke tests', 'build sanity suite', 'release validation'."
---

# Smoke Test Suite Builder

## Purpose
Post-deployment smoke testing is the final quality gate to verify that a release has succeeded and that core business functions are operational in the target environment. This skill automates the creation of lean, fast, and targeted smoke suites (scenarios, executable scripts, CI/CD configs, and readiness reports) designed to execute in under 5 minutes, maximizing post-deploy confidence while minimizing execution overhead.

## When to Use
Activate this skill when:
- Designing a fast validation suite to run immediately after a deployment or release.
- Setting up sanity test scripts to verify environment health (Staging, QA, Production).
- Creating automated checklists to run as a final quality gate in a CI/CD pipeline.
- Defining critical business workflows and mapping their post-deployment verification points.

## When NOT to Use
Do not activate this skill when:
- The goal is deep regression testing covering all boundary and negative cases (use `test-case-generator` instead).
- Troubleshooting flaky test execution or fixing existing scripts (use `flaky-test-and-self-healing` instead).
- Analyzing API contract mismatches against spec schemas (use `api-contract-tester` instead).
- Conducting load, stress, performance, or security penetration tests.

## Prerequisites
Before running the generated smoke tests, ensure the required CLI tools and libraries are installed:
- **Playwright (Web)**:
  ```bash
  pip install playwright pytest pytest-xdist
  playwright install chromium
  ```
- **Newman (API)**:
  ```bash
  npm install -g newman
  ```
- **Robot Framework (Web/Mobile)**:
  ```bash
  pip install robotframework robotframework-seleniumlibrary robotframework-appiumlibrary pabot
  ```

## Process
When building a smoke test suite, follow these steps:

1. **Analyze Application Context & Inputs**: Review the application name, type (Web, API, Mobile), features, user roles, technology stack, environment (Dev, QA, Staging, Prod), and any source artifacts (Swagger specs, existing test cases, automation scripts).
2. **Discover Critical Workflows & Release-Impact**: Identify key transactional paths (e.g., User Login, Checkout, API Authentication, Core Data Retrieval) that represent the highest business value and are most vulnerable to deployment failures.
3. **Define Smoke Test Scenarios**: Draft structured Given/When/Then scenarios or checklist items for the discovered workflows. Focus on happy paths and critical integration points, leaving deep edge cases to regression suites.
4. **Generate Executable Automation Scripts**: Generate clean, modular, and functional automation scripts tailored to the app type and framework requested (defaulting to Playwright Python for Web, Postman/Newman for API, and Appium Python for Mobile).
5. **Optimize for Speed (< 5 mins)**: Use parallel execution configurations, direct API seeding (to bypass slow UI flows), and minimal assertion paths to keep runtime under the 5-minute threshold.
6. **Configure CI/CD Integration**: Write clean execution commands and pipeline snippets (e.g., GitHub Actions, GitLab CI, AWS CodePipeline) to run the smoke tests automatically post-deployment. Refer to [ci-cd-examples.md](file:///c:/Users/costrategix/.gemini/antigravity-ide/brain/SkillCreatorPOC/.agents/skills/smoke-test-builder/references/ci-cd-examples.md) for pre-built templates.
7. **Produce Deployment Readiness Report**: Generate a formatted template that the release team can use to record test results, environment health, and sign-offs.

## Decision Rules and Conditional Logic
- **IF** the application type is **Web** **THEN** generate Playwright (Python/JS) or Robot Framework scripts targeting critical UI paths. Ensure locators follow the team's standard (avoiding fragile xpath/css paths, prioritizing ids/data-testid).
- **IF** the application type is **API** **THEN** generate Postman/Newman collection JSON or Python Requests scripts checking response codes (200/201), JSON schema compliance, and performance SLA latency (e.g., < 2s).
- **IF** the application type is **Mobile** **THEN** generate Appium Python or Robot Framework AppiumLibrary scripts specifying core Desired Capabilities (platformName, deviceName, appPackage, appActivity).
- **IF no command-line tools** are specified for execution **THEN** reference `pytest` for Playwright, `newman` for Postman collections, and `robot` for Robot Framework.
- **IF** no automation framework is specified **THEN** use **Playwright (Python)** for Web, **Newman/Postman** for API, and **Appium (Python)** for Mobile.
- **IF** source artifacts (OpenAPI spec/Swagger) are provided **THEN** parse endpoints, methods, and schemas to generate targeted API test requests.
- **IF** the target environment is **Production** **THEN** strictly generate non-destructive read-only tests (e.g., GET requests or viewing dashboard page) to avoid data pollution.

## Recommended Tools and Commands
To maintain smoke test efficiency, use the following tools and CLI commands:
- **Playwright (Web)**: Use the command `pytest --numprocesses auto` (parallel execution via pytest-xdist) to run UI checks concurrently.
- **Newman (API)**: Use the command `newman run collection.json --bail` to stop execution immediately on the first smoke test failure.
- **Robot Framework (Web/Mobile)**: Use the command `pabot --processes 4` (parallel Robot execution) to run `.robot` suites concurrently.
- **Verification Helper**: Use the command `python scripts/validate-smoke.py` to parse steps and flag execution bottlenecks.

## Output Format
Generate the smoke test suite in a clear, structured markdown format containing the following sections:

### 1. Document Title
`# Smoke Test Suite - [Application Name] ([Environment])`

### 2. Workflow Discovery & Impact Mapping
Include a table mapping workflows to post-deployment checks:
| Workflow ID | Business Workflow | Target Path / Endpoint | User Role | Speed Target | Post-Deploy Impact / Risk |
|---|---|---|---|---|---|

### 3. Smoke Test Scenarios (BDD/Checklist)
Describe the scenarios using Gherkin or clear checklists.

### 4. Executable Automation Script
Fenced code block containing the fully functional automation code (e.g., Playwright, Robot, Newman JSON). Ensure proper import statements, base URL parameterization, and modular functions.

### 5. Execution & CI/CD Pipeline Configuration
List the shell command to execute the test suite locally (e.g., `pytest test_smoke.py` or `newman run collection.json`).
Provide a complete CI/CD configuration block (e.g., GitHub Actions workflow or GitLab CI job) that triggers the smoke suite.

### 6. Deployment Readiness Report Template
A clear markdown template for the QA/Ops team to fill out after execution.

## Examples

### Example 1: Web Application (Playwright Python)
**Input**: Web E-Commerce portal, environment Staging, staging URL: `https://stage.shop.example.com`. Critical feature is user authentication, searching products, and viewing checkout. Tech Stack is Playwright Python.

**Output**:
```markdown
# Smoke Test Suite - E-Commerce Storefront (Staging)

## Workflow Discovery & Impact Mapping
| Workflow ID | Business Workflow | Target Path / Endpoint | User Role | Speed Target | Post-Deploy Impact / Risk |
|---|---|---|---|---|---|
| SMOKE-01 | User Login | /login | Customer | < 10s | Critical. Breakage prevents user access to checkout. |
| SMOKE-02 | Product Search | /search | Guest/Customer | < 5s | High. Mismatches block customers finding products. |
| SMOKE-03 | Add to Cart | /cart | Customer | < 5s | High. Cart failure directly blocks conversion. |
| SMOKE-04 | View Checkout | /checkout | Customer | < 5s | Critical. Page load failure blocks checkout. |

## Smoke Test Scenarios (BDD)
```gherkin
Scenario: Customer can authenticate and proceed to checkout
  Given the user is on the staging storefront login page "https://stage.shop.example.com/login"
  When they enter valid credentials and submit
  Then they are redirected to the homepage dashboard
  And they search for "laptop" and click on the first search result
  And they click "Add to Cart"
  And they navigate to the checkout page
  Then the checkout form elements should load successfully
```

## Executable Automation Script
```python
import os
import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = os.getenv("TARGET_URL", "https://stage.shop.example.com")
USERNAME = os.getenv("SMOKE_USER", "smoke_customer")
PASSWORD = os.getenv("SMOKE_PASSWORD", "SecurePass123!")

def test_ecommerce_smoke_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # 1. Login Page Sanity
        page.goto(f"{BASE_URL}/login")
        page.fill("input[name='username']", USERNAME)
        page.fill("input[name='password']", PASSWORD)
        page.click("button[type='submit']")
        
        # Verify redirect to dashboard
        expect(page).to_have_url(f"{BASE_URL}/dashboard")
        
        # 2. Product Search
        page.fill("input[name='q']", "laptop")
        page.press("input[name='q']", "Enter")
        page.click("a.product-item >> text=laptop")
        
        # 3. Add to Cart
        page.click("button.add-to-cart")
        expect(page.locator(".cart-badge")).to_contain_text("1")
        
        # 4. View Checkout
        page.goto(f"{BASE_URL}/checkout")
        expect(page.locator("h1")).to_contain_text("Checkout")
        expect(page.locator("button#place-order")).to_be_visible()
        
        context.close()
        browser.close()
```

## Execution & CI/CD Configuration
Run locally using:
```bash
pytest test_smoke.py
```

### GitHub Actions Integration
Add to `.github/workflows/smoke-test.yml`:
```yaml
name: Post-Deployment Smoke Test
on:
  deployment_status:
jobs:
  smoke-test:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Dependencies
        run: |
          pip install playwright pytest
          playwright install chromium
      - name: Run Smoke Tests
        env:
          TARGET_URL: ${{ github.event.deployment_status.target_url }}
          SMOKE_USER: ${{ secrets.SMOKE_USER }}
          SMOKE_PASSWORD: ${{ secrets.SMOKE_PASSWORD }}
        run: pytest test_smoke.py
```

## Deployment Readiness Report Template
| Metric / Check | Value / Result | Notes / Details |
|---|---|---|
| Deployment Target | Staging / Production | |
| Release Version | [e.g., v2.4.1] | |
| Execution Timestamp | [YYYY-MM-DD HH:MM] | |
| Smoke Suite Result | PASS / FAIL | |
| Executed By | Automation CI / QA Name | |
| Critical Flows OK? | Yes / No | |
| Sign-off | APPROVED / BLOCKED | |
```

### Example 2: API Application (Newman/Postman Collection)
**Input**: API Application, Staging, base URL: `https://api.stage.company.com/v1`. Endpoints: POST `/auth/login`, GET `/users/me`.

**Output**:
```markdown
# Smoke Test Suite - Profile API (Staging)

## Workflow Discovery & Impact Mapping
| Workflow ID | Business Workflow | Target Path | Method | Speed Target | Post-Deploy Impact |
|---|---|---|---|---|---|
| API-SMOKE-01 | Auth Login | /auth/login | POST | < 2s | Critical. Auth failures block all client integrations. |
| API-SMOKE-02 | Get Profile | /users/me | GET | < 1s | High. Prevents users from fetching profile info. |

## Smoke Test Scenarios
1. **Authentication Ping**: POST request to `/auth/login` returns a 200 OK status code, contains a valid `token` field in response JSON, and responds in under 2 seconds.
2. **Current User Profile Retrieval**: GET request to `/users/me` with bearer authorization token returns a 200 OK status code and is schema-compliant.

## Executable Automation Script
Save as `api_smoke_collection.json`:
```json
{
  "info": {
    "name": "API Smoke Suite",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth Login",
      "request": {
        "method": "POST",
        "header": [
          { "key": "Content-Type", "value": "application/json" }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"username\": \"{{SMOKE_USER}}\", \"password\": \"{{SMOKE_PASSWORD}}\"}"
        },
        "url": {
          "raw": "{{BASE_URL}}/auth/login"
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status is 200', function () { pm.response.to.have.status(200); });",
              "pm.test('Has access token', function () {",
              "  var jsonData = pm.response.json();",
              "  pm.expect(jsonData.token).to.not.be.undefined;",
              "  pm.globals.set('authToken', jsonData.token);",
              "});",
              "pm.test('Latency SLA check', function () { pm.expect(pm.response.responseTime).to.be.below(2000); });"
            ]
          }
        }
      ]
    },
    {
      "name": "Get User Profile",
      "request": {
        "method": "GET",
        "header": [
          { "key": "Authorization", "value": "Bearer {{authToken}}" }
        ],
        "url": {
          "raw": "{{BASE_URL}}/users/me"
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status is 200', function () { pm.response.to.have.status(200); });",
              "pm.test('Response matches schema', function () {",
              "  var jsonData = pm.response.json();",
              "  pm.expect(jsonData.email).to.be.a('string');",
              "  pm.expect(jsonData.id).to.be.a('number');",
              "});"
            ]
          }
        }
      ]
    }
  ]
}
```

## Execution & CI/CD Configuration
Run locally using newman:
```bash
newman run api_smoke_collection.json --env-var BASE_URL=https://api.stage.company.com/v1 --env-var SMOKE_USER=smoke_qa --env-var SMOKE_PASSWORD=secure_pass
```

### GitLab CI Integration
Add to `.gitlab-ci.yml`:
```yaml
stages:
  - post-deploy-smoke

run-smoke-tests:
  stage: post-deploy-smoke
  image: 
    name: postman/newman:latest
    entrypoint: [""]
  script:
    - newman run api_smoke_collection.json --env-var BASE_URL=$BASE_URL --env-var SMOKE_USER=$SMOKE_USER --env-var SMOKE_PASSWORD=$SMOKE_PASSWORD
  only:
    - triggers
```

## Deployment Readiness Report Template
| Metric / Check | Value / Result | Notes / Details |
|---|---|---|
| Deployment Target | Staging / Production | |
| Release Version | [e.g., v1.10.4] | |
| Execution Timestamp | [YYYY-MM-DD HH:MM] | |
| Smoke Suite Result | PASS / FAIL | |
| Total Executed | 2 / 2 Passed | |
| Sign-off | APPROVED / BLOCKED | |
```

## Anti-Patterns and Pitfalls
Avoid the following common mistakes:
- **Testing Exhaustive Edge Cases**: Smoke testing is not regression testing. Focus only on happy paths. Including too many edge cases increases execution time and delays release cycles.
- **Hardcoding Wait Times (sleep)**: Never use fixed sleeps. Use smart assertions or auto-waiting locators to speed up execution and reduce flakiness.
- **Data Pollution on Production**: Do not run destructive POST or DELETE operations in production. Ensure production smoke tests are read-only or run against isolated test accounts.
- **Ignoring Execution SLA**: Ensure the smoke suite completes in less than 5 minutes. If it runs slower, optimize by implementing parallel execution or mocking external dependencies.

## Edge Cases
- **Ambiguous or Missing Specs**: If no target URLs or user details are provided, default to creating a basic health ping check (GET `/health` or home page load check) and prompting the user for transactional data.
- **Authentication Timeout**: Ensure scripts handle token expiration gracefully by initiating auth sequences before transactional requests.
- **Slow Dynamic Loading**: Encourage the use of auto-waiting and retry assertions (e.g., Playwright's `expect` or Robot's `Wait Until Element Is Visible`) instead of hardcoded timeouts (`sleep`) to minimize execution duration.

## Changelog
- **v1.0** (2026-06-19)
  - Initial release of the `smoke-test-builder` skill.
  - Added full support for Web, API, and Mobile app smoke test suites.
  - Integrated CI/CD configuration guidelines and execution time optimization rules.