---
name: robot-framework-tester
description: "Generate production-ready Robot Framework test suites for Web UI testing (SeleniumLibrary) and REST API testing (RequestsLibrary). Produces .robot files with Settings/Variables/Test Cases/Keywords, .resource Page Object files, and Python .py helper libraries. Follows team conventions: suite setup/teardown, data-driven templates, proper waits (never Sleep), screenshots on failure, headless CI, session-based API tests, and tags (smoke, regression, critical). Trigger on: write robot tests, create robot framework test suite, generate .robot file, build selenium tests, automate this page with robot, write API tests with RequestsLibrary, create resource file, generate data-driven robot tests, scaffold robot project, convert manual test cases into robot scripts. Do NOT trigger for BDD test case docs from user stories (use test-case-generator), API contract validation against Swagger (use api-contract-tester), debugging failing robot tests, writing pytest unit tests, or CI/CD pipeline config."
metadata:
  author: QA Skills Team
  version: 1.0.0
  category: quality-assurance
---

# Robot Framework Test Generator

## Purpose

This skill generates complete, executable Robot Framework test suites from
feature descriptions, user stories, or manual test case documents. It produces
three types of files that work together:

1. **`.robot` test files** — structured suites with proper Settings, Variables,
   Test Cases, and Keywords sections
2. **`.resource` files** — reusable Page Object keyword libraries, one per page
   or API domain
3. **`.py` helper scripts** — Python libraries for complex data generation,
   custom keywords, or logic that is awkward to express in Robot syntax

The output is ready to run in CI pipelines with headless browser support and
follows the team's established conventions for naming, tagging, waits, and
project structure.

## When to Use

### Activate this skill when the user:

- Asks to **write**, **create**, or **generate** Robot Framework test files
- Wants to **automate a web page** or **UI flow** using SeleniumLibrary
- Wants to **automate REST API tests** using RequestsLibrary
- Needs a **Page Object `.resource` file** for a specific page or component
- Asks for **data-driven test templates** in Robot Framework syntax
- Wants to **convert manual test cases** or Gherkin scenarios into `.robot` scripts
- Needs a **Python custom keyword library** for Robot Framework
- Asks to **scaffold a Robot Framework test project** structure

### Do NOT activate when the user:

- Wants **BDD test case documentation** from user stories (use `test-case-generator`)
- Wants to **validate API responses against Swagger/OpenAPI** specs (use `api-contract-tester`)
- Is **debugging a failing Robot Framework test** (e.g., fixing `ElementNotFound`, analyzing `output.xml`)
- Is writing **Python unit tests** with `pytest` or `unittest`
- Needs help with **CI/CD pipeline configuration** (Jenkins, GitHub Actions YAML)
- Is **reviewing or refactoring** existing `.robot` files

## Decision Logic: SeleniumLibrary vs RequestsLibrary vs Both

- **IF** the feature involves a browser-rendered UI (pages, forms, buttons,
  navigation) **THEN** use **SeleniumLibrary**. Read `references/ui-test-template.robot`
  and `references/page-object-template.resource` for the base templates.
- **IF** the feature is a pure REST API (endpoints, JSON payloads, status codes)
  **THEN** use **RequestsLibrary**. Read `references/api-test-template.robot`.
- **IF** the feature involves both UI and API **THEN** import both libraries.
  Use RequestsLibrary for setup/seeding/verification and SeleniumLibrary for
  UI interaction.
- **IF** the user does not specify **THEN** ask: *"Does this feature have a
  web UI, is it API-only, or does it need both?"*

## Process

1. **Parse the input and determine scope.**
   Extract the feature name, pages/endpoints involved, user roles, and test
   data requirements. If the input is vague (e.g., "write tests for login"),
   ask for specifics: What fields? What validation rules? What error messages?

2. **Decide the test type** using the decision logic above (UI, API, or both).

3. **Design the project structure.**
   Plan which files to create:
   - One `.robot` suite file per feature or page
   - One `.resource` file per page (Page Object pattern)
   - One `variables.robot` or `variables.yaml` for environment-specific values
   - Python `.py` files only when logic is too complex for Robot syntax

4. **Generate the `.resource` file(s) first** — Page Object keywords.
   Read `references/page-object-template.resource` for the structure. Each keyword:
   - Has a clear, action-oriented name (e.g., `Fill Login Form`)
   - Uses proper waits (`Wait Until Element Is Visible`) not `Sleep`
   - Accepts parameters for test data flexibility
   - Includes `[Documentation]` explaining what the keyword does

5. **Generate the `.robot` test suite file.**
   Read `references/ui-test-template.robot` or `references/api-test-template.robot`.
   Structure with all four sections. Use tags for categorization. Include
   Suite Setup/Teardown for browser lifecycle. Use `[Template]` for data-driven tests.

6. **Generate Python helper scripts** if needed.
   Read `references/python-helper-template.py` for the structure. Create `.py`
   files for data generation, complex assertions, or custom keyword libraries.

7. **Review for anti-patterns** (see below) and fix any violations.

## Output Format

### Project Structure

```
tests/
├── <feature_name>.robot          # Test suite
├── resources/
│   ├── <page_name>_page.resource # Page Object keywords
│   └── common.resource           # Shared keywords (login, nav)
├── variables/
│   └── variables.robot           # OR variables.yaml
└── libraries/
    └── <helper_name>.py          # Python helpers (when needed)
```

### Templates

Read these reference files when generating output — they contain the full
annotated templates with all required sections and conventions:

| File Type           | Template Reference                              |
|--------------------|-------------------------------------------------|
| UI test suite      | `references/ui-test-template.robot`             |
| API test suite     | `references/api-test-template.robot`            |
| Page Object        | `references/page-object-template.resource`      |
| Variables          | `references/variables-template.robot`           |
| Python helper      | `references/python-helper-template.py`          |

### Reference Guides & Helper Scripts

Refer to these files for installation, configuration, debugging, and advanced patterns:

- **[QA Playbook](file:///c:/Users/costrategix/PycharmProjects/qa-skills-repo/.agent/skills/robot-framework-tester/references/playbook.md)** — Complete implementation guide, dependency pinning, local commands, Selenium Grid settings, a debugging table for 12+ common errors, and best practices.
- **[Advanced Patterns](file:///c:/Users/costrategix/PycharmProjects/qa-skills-repo/.agent/skills/robot-framework-tester/references/advanced-patterns.md)** — Advanced techniques including DataDriver (CSV), YAML variables, parallel execution browser matrix, database verification, complex native keywords, custom Python listeners, and environment-specific variable files.
- **[Test Runner Script](file:///c:/Users/costrategix/PycharmProjects/qa-skills-repo/.agent/skills/robot-framework-tester/scripts/run_tests.py)** — Helper script providing execution commands (full suite, tags, pabot parallel runs, and reporting).

## Naming Conventions

| Element              | Convention                     | Example                          |
|---------------------|-------------------------------|----------------------------------|
| Test suite file     | `snake_case.robot`            | `user_login.robot`               |
| Resource file       | `<page>_page.resource`        | `login_page.resource`            |
| Python library      | `PascalCase.py`               | `DataGenerator.py`               |
| Test case name      | Title Case, descriptive       | `Verify Login With Valid Creds`  |
| Keyword name        | Title Case, action-oriented   | `Fill Login Form`                |
| Variable (global)   | `${UPPER_SNAKE_CASE}`         | `${BASE_URL}`                    |
| Variable (local)    | `${lower_snake_case}`         | `${response}`                    |
| Locator variable    | `${ELEMENT_TYPE_NAME}`        | `${BTN_SUBMIT}`                  |
| Tag                 | lowercase, hyphenated         | `smoke`, `regression`            |

## Tag Strategy

| Tag          | Purpose                                      |
|-------------|----------------------------------------------|
| `smoke`     | Minimal verification — run on every deploy    |
| `regression`| Full coverage — run nightly or pre-release    |
| `critical`  | Business-critical — failure blocks release    |
| `high`      | Important — investigate promptly              |
| `medium`    | Standard coverage — normal priority           |
| `low`       | Nice-to-have — edge cases and cosmetic checks |
| `api`       | API-only tests (no browser needed)            |
| `ui`        | Browser-based UI tests                        |
| `data-driven`| Template-based parameterized tests           |
| `wip`       | Work in progress — excluded from CI runs      |

## Examples

### Example 1: Web UI Login Page

**Input:** "Write robot framework tests for our login page. It has email and
password fields, a submit button, and shows 'Invalid credentials' on failure.
Account locks after 5 bad attempts."

**Output files:**

1. `tests/resources/login_page.resource` — locators and keywords for the login page
2. `tests/variables/variables.robot` — URLs, credentials, timeouts
3. `tests/user_login.robot` — test suite with smoke, positive, negative,
   boundary (5th attempt lockout), and data-driven invalid input tests
4. `tests/libraries/DataGenerator.py` — generates random email/password test data

### Example 2: REST API CRUD Endpoints

**Input:** "Generate robot tests for our user management API. POST /api/users
creates a user (name, email required). GET /api/users/{id} returns user.
DELETE /api/users/{id} removes user. Auth is Bearer token."

**Output files:**

1. `tests/variables/variables.robot` — API base URL, auth token
2. `tests/user_api.robot` — full API test suite with session management:
   create, read, delete, plus negative tests (missing fields, duplicate email)
3. `tests/libraries/ApiHelpers.py` — generates test payloads, cleanup utilities

### Example 3: Combined UI + API Test

**Input:** "Write tests for our product search. The UI has a search bar on
/products, and results come from GET /api/products?q=. Verify both the UI
rendering and the API response."

**Output files:**

1. `tests/resources/search_page.resource` — UI locators and keywords
2. `tests/variables/variables.robot` — URLs, test search terms
3. `tests/product_search.robot` — imports both SeleniumLibrary and
   RequestsLibrary; API keywords seed data, UI keywords verify rendering

## Anti-Patterns

Avoid these common mistakes in all generated code:

### Never use `Sleep` for synchronization
`Sleep` creates brittle tests — either too slow (wasting CI time) or too fast
(flaky failures). Use `Wait Until Element Is Visible`, `Wait Until Page Contains`,
or similar explicit waits that adapt to actual page state.

### Never hardcode locators in test cases
Locators belong in `.resource` files. When the UI changes, update one file —
not every test that touches that element. Test cases should call Page Object
keywords like `Fill Login Form`, not `Input Text    id:username`.

### Never skip `[Documentation]`
Every test case and keyword needs `[Documentation]`. Tests without it become
incomprehensible within weeks. Document *why* the test exists.

### Never use XPath when simpler locators work
Use `id` first, `css` second, `xpath` only for complex DOM traversal. XPath
is fragile, hard to read, and slower.

### Never create one giant `.robot` file
Split tests by feature or page. A 500-line `.robot` file needs decomposition.

### Never ignore test teardown for failure screenshots
Always include: `Test Teardown    Run Keyword If Test Failed    Capture Page Screenshot`.
Without this, debugging CI failures requires local reproduction.

### Never use `Create Webdriver` when `Open Browser` suffices
`Open Browser` handles browser options cleanly. Use it with headless args:
`options=add_argument("--headless");add_argument("--no-sandbox")`

### Never call APIs without session management
Use `Create Session` + `GET On Session` / `POST On Session`. Sessions reuse
TCP connections and auth headers. Raw `GET`/`POST` without sessions creates
new connections and requires repeating headers.

## Edge Cases

**Vague input ("write tests for the homepage"):**
Ask for specifics before generating. Which elements? What interactions?
Generate a skeleton with `TODO` comments only if explicitly asked.

**Feature with no UI and no API:**
Explain that Robot Framework is not the right tool for purely backend logic.
Suggest pytest or shell scripts instead.

**Legacy page with dynamic IDs:**
Use CSS class selectors, `data-testid` attributes, or relative XPath. Add a
comment in the `.resource` file noting the locator fragility.

**Mixed auth patterns:**
If UI uses session cookies but API uses Bearer tokens, generate separate
setup keywords. Do not share auth state between libraries.

**Large test data sets (50+ rows):**
Generate a separate `.csv` or `.yaml` data file and use DataDriver library
instead of inline `[Template]` tables.

## Changelog

- **v1.1.0** (2026-05-29)
  - Fixed frontmatter YAML parsing description formatting issues.
  - Added [QA Playbook](file:///c:/Users/costrategix/PycharmProjects/qa-skills-repo/.agent/skills/robot-framework-tester/references/playbook.md) guide with dependencies, local execution, Selenium Grid, 13 debugging error solutions, and 14+ best practices.
  - Added [Advanced Patterns](file:///c:/Users/costrategix/PycharmProjects/qa-skills-repo/.agent/skills/robot-framework-tester/references/advanced-patterns.md) guide covering DataDriver, database verification, listener logic, environment-specific variable files.
  - Created executable [Test Runner Script](file:///c:/Users/costrategix/PycharmProjects/qa-skills-repo/.agent/skills/robot-framework-tester/scripts/run_tests.py) to run test suites.
- **v1.0.0** (2026-05-29)
  - Initial release of `robot-framework-tester` skill.
  - Web UI testing with SeleniumLibrary and Page Object pattern.
  - API testing with RequestsLibrary and session management.
  - Data-driven testing with `[Template]` keyword pattern.
  - Python helper script generation for custom keyword libraries.
  - Anti-patterns section covering 8 common mistakes.
  - CI-friendly defaults (headless browser, screenshot on failure).

## References

- [Robot Framework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [SeleniumLibrary Keywords](https://robotframework.org/SeleniumLibrary/SeleniumLibrary.html)
- [RequestsLibrary Keywords](https://marketsquare.github.io/robotframework-requests/doc/RequestsLibrary.html)
- [Pabot Parallel Executor](https://pabot.org/)
