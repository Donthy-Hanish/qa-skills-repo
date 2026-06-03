# Change Impact Report

## Change Summary

| Field | Value |
|-------|-------|
| Change ID | _[Jira ticket ID, PR number, or "Free-text"]_ |
| Change Title | _[One-line summary of the change]_ |
| Input Type | _[Jira Ticket / Diff-PR / Free-Text / Combined]_ |
| Analysis Date | _[YYYY-MM-DD]_ |
| Analyst | _[Name or "Automated"]_ |

## Change Description

_[2-3 sentence summary of what the change does and why.]_

## Affected Areas

| # | Area / Module | Impact Type | Risk Level | Risk Rationale |
|---|---------------|-------------|------------|----------------|
| 1 | _[e.g., Auth Middleware]_ | _[Direct / Upstream / Downstream / Shared]_ | _[Critical / High / Medium / Low]_ | _[One sentence explaining why this risk level]_ |
| 2 | | | | |
| 3 | | | | |

## Tests to Run

_If no project test map is loaded, this section will state so explicitly and will
NOT list fabricated test IDs._

### By Priority

**Critical Risk Areas:**
- _[Area name]_: _[Test IDs or tags, or "No mapped tests - see Coverage Gaps"]_

**High Risk Areas:**
- _[Area name]_: _[Test IDs or tags, or "No mapped tests - see Coverage Gaps"]_

**Medium Risk Areas:**
- _[Area name]_: _[Test IDs or tags, or "No mapped tests - see Coverage Gaps"]_

**Low Risk Areas:**
- _[Area name]_: _[Test IDs or tags, or "No mapped tests - see Coverage Gaps"]_

### Automated Suites

| Suite / Tag | Estimated Run Time | Covers |
|-------------|-------------------|--------|
| _[e.g., @auth]_ | _[e.g., 10 min]_ | _[e.g., Auth middleware, login, logout]_ |

### Manual Tests

| Test ID | Test Name | Module | Priority |
|---------|-----------|--------|----------|
| _[e.g., TC-101]_ | _[e.g., Login with valid credentials]_ | _[e.g., Auth]_ | _[e.g., Critical]_ |

## Regression Scope Recommendation

| Field | Value |
|-------|-------|
| Recommended Scope | _[Smoke / Sanity / Targeted Regression / Full Regression]_ |
| Rationale | _[2-3 sentences explaining why this scope level]_ |
| Estimated Effort | _[e.g., "2 hours manual + 30 min automated" or "Unknown - no test map loaded"]_ |

## Coverage Gaps

| # | Area | Why Affected | Risk Introduced | Suggested Test Type |
|---|------|-------------|-----------------|---------------------|
| 1 | _[e.g., New push notification channel]_ | _[e.g., Net-new code path with no existing tests]_ | _[e.g., Silent failure if device token is missing]_ | _[e.g., Integration test]_ |
| 2 | | | | |

## Notes and Caveats

- _[Any assumptions made during analysis]_
- _[Any areas where the analyst lacked information]_
- _[Recommendations for follow-up]_
