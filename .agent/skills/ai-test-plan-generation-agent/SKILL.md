---
name: ai-test-plan-generation-agent
description: "Generate QA test plans, strategies, and scenarios. Trigger when asked to generate a test plan, write a test strategy, design test scenarios, or create smoke/regression suites."
---

# AI Test Plan Generation Agent

## Purpose
To transform requirements into a structured test strategy and complete test plan, defining specific test suites and scenarios covering all testing types.

## Process
1. Read the requirements document (e.g., `specs/requirements.md`).
2. Create a comprehensive QA Test Strategy and Test Plan containing:
   - A. Scope
   - B. Out of Scope
   - C. Assumptions
   - D. Risks
   - E. Entry Criteria
   - F. Exit Criteria
   - G. Test Strategy
   - H. Environment Requirements
3. Create Test Scenarios for:
   - 1. Functional Testing, 2. UI Testing, 3. Exploratory Testing, 4. Integration Testing, 5. API Testing, 6. Regression Testing, 7. Smoke Testing, 8. Security Testing, 9. Accessibility Testing, 10. Responsive Testing, 11. Cross Browser Testing, 12. Negative Testing, 13. Boundary Testing
4. For each scenario, define:
   - Test Case ID
   - Scenario Name
   - Priority
   - Preconditions
   - Test Steps
   - Expected Results
5. Organize scenarios into suites:
   - Smoke Suite
   - Regression Suite
   - Critical Path Suite
   - High Risk Suite
6. Save the output to `specs/test-plan.md`.

## Output Format
Structured markdown saved to `specs/test-plan.md` containing all strategy headers, scenario matrices, and test suite groupings.

## Examples
### Example 1
**Input requirements.md snippet**: "REQ-01: User Login"
**Output test-plan.md**:
```markdown
# QA Test Plan

## 1. Scope
...

## 2. Test Scenarios
| Test Case ID | Scenario Name | Priority | Preconditions | Test Steps | Expected Results |
|---|---|---|---|---|---|
| TC-LOG-01 | Valid Login | Critical | User registered | 1. Go to URL... | Dashboard loaded |
```

## Edge Cases
- **Missing Requirements**: If `specs/requirements.md` doesn't exist, search for user stories or read input directly, or prompt to run Step 1.
- **Complex UI controls**: Ensure detailed steps for intricate third-party widgets.
