# Project Test Map Template

Copy this file to `references/project-test-map.md` and fill in the sections below
for your project. This map connects modules to their test inventories, enabling the
change-impact analyzer to recommend specific tests for each affected area.

---

## Project Metadata

| Field | Value |
|-------|-------|
| Project Name | _[e.g., MyApp]_ |
| Jira Project Key | _[e.g., MYAPP]_ |
| Test Management Tool | _[e.g., Zephyr Scale, Xray, TestRail, none]_ |
| Automation Framework | _[e.g., Playwright, Cypress, Robot Framework, pytest, none]_ |
| Automation Repo | _[e.g., github.com/org/myapp-tests]_ |
| CI Platform | _[e.g., GitHub Actions, Jenkins, Azure DevOps, none]_ |

---

## Module Inventory

List every module, component, or subsystem. Each row maps a module to its Jira
components/labels, its automated test location, and its CI pipeline (if applicable).

| Module Name | Jira Component(s) | Jira Labels | Automated Test Path or Tag | CI Pipeline / Job Name | Notes |
|-------------|-------------------|-------------|---------------------------|----------------------|-------|
| _[e.g., User Management]_ | _[e.g., Auth, User-Profile]_ | _[e.g., user, auth]_ | _[e.g., tests/e2e/user/ or @user]_ | _[e.g., ci-user-tests]_ | _[e.g., Includes SSO integration]_ |
| _[e.g., Billing]_ | _[e.g., Billing, Payments]_ | _[e.g., billing, stripe]_ | _[e.g., tests/e2e/billing/]_ | _[e.g., ci-billing-tests]_ | _[e.g., Stripe webhook tests need sandbox]_ |
| | | | | | |
| | | | | | |
| | | | | | |

---

## Dependency Map

For each module, list what it depends on (upstream) and what depends on it
(downstream). This helps the analyzer trace blast radius.

| Module | Depends On (upstream) | Depended On By (downstream) |
|--------|----------------------|----------------------------|
| _[e.g., User Management]_ | _[e.g., Database, Email Service]_ | _[e.g., Billing, Notifications, Admin Panel]_ |
| _[e.g., Billing]_ | _[e.g., User Management, Payment Gateway]_ | _[e.g., Reports, Invoicing]_ |
| | | |
| | | |

---

## Test Suite Tags

If your automation framework uses tags or markers to group tests, list the key ones
here. This lets the analyzer recommend specific tags to run.

| Tag / Marker | What it covers | Approximate run time |
|-------------|----------------|---------------------|
| _[e.g., @smoke]_ | _[e.g., Core login, search, checkout paths]_ | _[e.g., 3 min]_ |
| _[e.g., @sanity]_ | _[e.g., Smoke + CRUD operations for each module]_ | _[e.g., 15 min]_ |
| _[e.g., @regression]_ | _[e.g., Full suite including edge cases]_ | _[e.g., 90 min]_ |
| _[e.g., @billing]_ | _[e.g., All billing and payment flows]_ | _[e.g., 20 min]_ |
| | | |

---

## Jira Test Case Mapping

If you use Zephyr, Xray, or another Jira-integrated test management tool, map
components to their test case folders or test cycles here.

| Jira Component | Test Folder / Cycle | Key Test Case IDs | Notes |
|---------------|--------------------|--------------------|-------|
| _[e.g., Auth]_ | _[e.g., Folder: Auth Tests / Cycle: Sprint-42-Auth]_ | _[e.g., TC-101, TC-102, TC-103]_ | _[e.g., TC-103 covers MFA]_ |
| _[e.g., Billing]_ | _[e.g., Folder: Billing Tests]_ | _[e.g., TC-201 through TC-215]_ | _[e.g., TC-210 needs Stripe sandbox]_ |
| | | | |

---

## Cross-Cutting Concerns

List shared resources, config files, and cross-cutting code that affect multiple
modules. The analyzer uses this to widen blast radius when these are touched.

| Shared Resource | Type | Modules Affected | Test Coverage |
|-----------------|------|-----------------|---------------|
| _[e.g., .env.production]_ | _[e.g., Config]_ | _[e.g., All]_ | _[e.g., Manual verification only]_ |
| _[e.g., src/middleware/auth.ts]_ | _[e.g., Code]_ | _[e.g., All authenticated endpoints]_ | _[e.g., @auth tag, TC-101 to TC-105]_ |
| _[e.g., db/migrations/]_ | _[e.g., Schema]_ | _[e.g., All data-layer modules]_ | _[e.g., Migration rollback test in CI]_ |
| | | | |

---

## Filling Instructions

1. Start with the Module Inventory - list every distinct area of your application.
2. For each module, fill in the Jira component(s) that map to it. These are the
   component tags on your Jira tickets.
3. Add the automated test path or tag for each module. If you use folder-based
   organization, give the path. If tag-based, give the tag.
4. Fill in the Dependency Map so the analyzer can trace upstream and downstream
   impact.
5. Add your test suite tags and Jira test case mappings.
6. List cross-cutting concerns last - these are the multipliers that widen blast
   radius.

Keep this file updated as your project evolves. When modules are added, renamed,
or deprecated, update the map so the analyzer stays accurate.
