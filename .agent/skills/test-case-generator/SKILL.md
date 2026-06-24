---
name: test-case-generator
description: "Generate Gherkin BDD test cases from user stories: positive, negative, boundary, and edge cases with Given/When/Then for Robot Framework. Triggers on: test cases, BDD, Jira tickets."
metadata:
  author: QA Skills Team
  version: 1.0.0
  category: quality-assurance
---

# Test Case Generator

## Purpose

This skill transforms user stories — whether pasted from Jira, copied from
Confluence, or typed as plain text — into a structured set of Gherkin-style BDD
test scenarios. It ensures thorough test coverage by systematically generating
positive, negative, boundary, and edge-case scenarios that a manual review
might overlook.

The output is formatted for teams using **Robot Framework with Selenium Python**,
using the Given/When/Then BDD keyword style that Robot Framework supports
natively. Each scenario includes priority, preconditions, and clear expected
results so the test cases are immediately actionable.

## When to Use

Activate this skill when the user:

- Asks to **generate**, **create**, or **write** test cases from a user story or acceptance criteria
- Pastes a **Jira ticket**, **Azure DevOps work item**, or **Confluence page** and asks for test scenarios
- Wants **BDD scenarios** (Given/When/Then) for a feature
- Needs **positive, negative, boundary, or edge-case** coverage for a story
- Asks what test cases they need for a feature or sprint item
- Wants test cases formatted for **Robot Framework** (`.robot` files) with **SeleniumLibrary** or **RequestsLibrary**

Do **NOT** activate when the user:

- Is debugging a failing test (e.g., fixing a `TimeoutError` in a `.robot` or `.py` file)
- Wants to review or refactor existing test scripts (`.robot`, `.py`, `.resource` files)
- Needs help with Robot Framework setup, Selenium grid config, or `pip install` commands
- Is writing Python unit tests with `pytest` or `unittest` (not BDD from stories)
- Asks about CI/CD pipelines, test reporting, or `output.xml` / `report.html` generation

## Tools and Frameworks

This skill is tailored for the following stack:

- **Robot Framework** — test automation framework using keyword-driven and BDD syntax
- **SeleniumLibrary** — Robot Framework library for browser-based UI testing via Selenium WebDriver
- **RequestsLibrary** — Robot Framework library for REST API testing (used for API-only stories)
- **Python 3** — underlying language for custom keywords and libraries
- **Browser/WebDriver** — Chrome, Firefox, or Edge via Selenium for UI test execution

### File types this skill produces or references:

| Extension    | Purpose                                           |
|-------------|---------------------------------------------------|
| `.md`       | Test case documentation output (the primary deliverable) |
| `.robot`    | Robot Framework test suite files (keyword reference)     |
| `.resource` | Robot Framework shared resource/keyword files            |
| `.py`       | Python custom keyword libraries for complex logic        |

## Process

1. **Parse the user story input.**
   Extract the key components from whatever format the user provides:
   - **Title / Story ID** (e.g., JIRA-1234)
   - **As a / I want / So that** (the user story statement)
   - **Acceptance criteria** (the conditions of satisfaction)
   - **Additional context** (UI mockups, API specs, business rules mentioned)

   If the input is incomplete — for example, a one-liner with no acceptance
   criteria — ask the user to provide more detail before proceeding. A vague
   input produces vague test cases, which wastes everyone's time.

2. **Identify the feature scope and actors.**
   Determine:
   - The feature or module under test (e.g., "Checkout Flow", "User Registration")
   - The primary actor (e.g., "logged-in customer", "admin user", "guest")
   - Key data entities involved (e.g., "order", "payment method", "product")
   - System integrations touched (e.g., "payment gateway", "email service")

3. **Generate positive test scenarios (happy path).**
   Cover every acceptance criterion with at least one scenario that validates
   the expected behavior when everything goes right. These are the scenarios
   that confirm the feature works as designed.

4. **Generate negative test scenarios.**
   For each positive scenario, think about what could go wrong:
   - Invalid input data (wrong format, missing required fields)
   - Unauthorized access (wrong role, expired session)
   - Business rule violations (exceeding limits, duplicate entries)
   - Dependency failures (API timeout, service unavailable)

5. **Generate boundary test scenarios.**
   Identify numeric, string-length, date, and quantity boundaries:
   - Minimum and maximum allowed values
   - Just below minimum, just above maximum
   - Empty vs. whitespace-only vs. single-character inputs
   - Date boundaries (past dates, future dates, leap years)

6. **Generate edge-case scenarios.**
   Think about the unusual situations:
   - Concurrent actions (two users editing the same record)
   - Special characters and Unicode in text fields
   - Browser-specific behavior (if UI testing is involved)
   - State transitions (what if the user refreshes mid-flow?)
   - Large data volumes (pagination, scroll performance)

7. **Format and present the output.**
   Organize all scenarios using the output format template below. Group by
   test type (positive, negative, boundary, edge). Assign priority levels
   (Critical, High, Medium, Low) based on business impact and likelihood.

## Output Format

Present the test cases using this structure:

```markdown
# Test Cases: [Feature Name]
**Source:** [Story ID or description]
**Generated:** [Date]
**Framework:** Robot Framework (BDD)

---

## Summary
| Type     | Count | Critical | High | Medium | Low |
|----------|-------|----------|------|--------|-----|
| Positive |       |          |      |        |     |
| Negative |       |          |      |        |     |
| Boundary |       |          |      |        |     |
| Edge Case|       |          |      |        |     |
| **Total**|       |          |      |        |     |

---

## Positive Test Scenarios

### TC-001: [Descriptive scenario title]
**Priority:** Critical | High | Medium | Low
**Preconditions:**
- [List any required state or setup]

**Scenario:**
```gherkin
Given [initial context]
And [additional context if needed]
When [action performed]
And [additional action if needed]
Then [expected outcome]
And [additional verification if needed]
```

**Test Data:**
| Field | Value | Notes |
|-------|-------|-------|
|       |       |       |

**Robot Framework Keywords (reference):**
```robot
*** Test Cases ***
TC-001 [Descriptive scenario title]
    [Documentation]    [Brief description]
    [Tags]    positive    critical    [feature-tag]
    Given [initial context]
    And [additional context if needed]
    When [action performed]
    Then [expected outcome]
```

---

## Negative Test Scenarios
[Same structure as above]

## Boundary Test Scenarios
[Same structure as above]

## Edge Case Scenarios
[Same structure as above]

---

## Traceability Matrix
| Test Case | Acceptance Criteria | Type     | Priority |
|-----------|-------------------|----------|----------|
| TC-001    | AC-1              | Positive | Critical |
| TC-002    | AC-1              | Negative | High     |
```

## Examples

### Example 1: Simple Login User Story

**Input:**
```
User Story: As a registered user, I want to log in with my email and password
so that I can access my dashboard.

Acceptance Criteria:
- User can log in with valid email and password
- System shows error for invalid credentials
- Account locks after 5 failed attempts
```

**Output (abbreviated):**

```markdown
# Test Cases: User Login
**Source:** Login User Story
**Framework:** Robot Framework (BDD)

## Positive Test Scenarios

### TC-001: Successful login with valid credentials
**Priority:** Critical
**Preconditions:**
- User has a registered account with verified email

**Scenario:**
```gherkin
Given the user is on the login page
And the user has a registered account with email "user@example.com"
When the user enters email "user@example.com"
And the user enters password "ValidPass123!"
And the user clicks the Login button
Then the user should be redirected to the dashboard
And the dashboard should display the user's name
```

## Negative Test Scenarios

### TC-004: Login with incorrect password
**Priority:** High
**Preconditions:**
- User has a registered account

**Scenario:**
```gherkin
Given the user is on the login page
When the user enters email "user@example.com"
And the user enters password "WrongPassword"
And the user clicks the Login button
Then the system should display error message "Invalid email or password"
And the user should remain on the login page
```

## Boundary Test Scenarios

### TC-008: Account lockout on 5th failed attempt
**Priority:** Critical
**Preconditions:**
- User has a registered account
- User has 4 prior failed login attempts

**Scenario:**
```gherkin
Given the user is on the login page
And the user has 4 failed login attempts
When the user enters incorrect credentials for the 5th time
Then the account should be locked
And the system should display "Account locked. Contact support."
```
```

### Example 2: User Story Pasted from Jira

**Input:**
```
PROJ-2847: Shopping Cart - Apply Discount Coupon

As a customer, I want to apply a discount coupon to my shopping cart
so that I can get a reduced price on my order.

Acceptance Criteria:
1. User can enter a valid coupon code and see the discount applied
2. Only one coupon per order
3. Expired coupons show an appropriate error
4. Coupon discount cannot exceed order total
```

**Output would include:**
- **Positive:** Valid coupon applied, discount reflected in total
- **Negative:** Expired coupon rejected, second coupon blocked, invalid code
- **Boundary:** Coupon value equals order total, coupon value exceeds total (capped at order total), minimum order threshold
- **Edge Case:** Applying coupon then removing items below threshold, coupon with special characters in code, applying coupon during flash sale overlap

---

### Example 3: Vague Input Handling

**Input:**
```
"Generate test cases for user registration"
```

**Response:**
Before generating test cases, ask:
- What fields are required for registration? (name, email, password, phone?)
- Are there password complexity requirements?
- Is email verification required?
- Is there social login (Google, GitHub)?
- What's the minimum age requirement, if any?

This avoids generating generic test cases that don't match the actual implementation.

## Edge Cases

**Incomplete user stories:**
If the user provides a story with no acceptance criteria, ask for them. Don't
guess — acceptance criteria define what "done" means, and guessing leads to
test cases that test the wrong things. Prompt the user: *"This story doesn't
have acceptance criteria. Could you list the conditions that must be true for
this story to be considered complete?"*

**Overly broad stories:**
If a story covers too much scope (e.g., "As a user, I want to manage my
account"), suggest breaking it into smaller stories first. Generating 50+ test
cases from a single story usually means the story is an epic in disguise.

**Non-functional requirements:**
If the user story implies performance, security, or accessibility requirements,
call them out but generate them as a separate section. These often need
different tooling (e.g., load tests with Locust, security scans with OWASP ZAP)
and shouldn't be mixed with functional BDD scenarios.

**API-only stories (no UI):**
If the story is about an API endpoint with no UI, adapt the Given/When/Then
to use API-oriented language (e.g., "Given the API endpoint /users is available"
instead of "Given the user is on the registration page"). Note that Robot
Framework's RequestsLibrary is used instead of SeleniumLibrary for these cases.

**Multiple user roles:**
If the story involves different user roles (admin, regular user, guest),
generate separate scenario groups per role. What an admin can do and what a
guest can do with the same feature are fundamentally different test paths.
