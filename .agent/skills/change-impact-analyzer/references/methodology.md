# Change Impact Analysis Methodology

This document defines the step-by-step reasoning framework for analyzing the impact
of a code change. Read this at the start of every analysis run.

## 1. Input Classification

Every analysis begins by classifying the input into one or more types:

| Input Type | Key Signals | Primary Value |
|------------|-------------|---------------|
| Jira ticket | Summary, Description, Components, Labels, Fix Version, Linked Issues | Intent, scope, component tags, business context |
| Diff / PR | Changed files, added/removed lines, function signatures | Precise file-level and function-level change data |
| Free-text | Natural language description of what changed | Intent and business context, but less precision |

When multiple inputs are available, layer them: the diff provides precision (what
exactly changed), the ticket provides context (why it changed and what it connects
to), and free-text fills gaps.

## 2. Signal Extraction

### From Jira Tickets

Extract these structured signals:

- **Components**: Direct module mapping. Each component typically corresponds to a
  module or subsystem in the codebase.
- **Labels**: Risk and category signals. Common high-signal labels include:
  `breaking-change`, `security`, `migration`, `high-risk`, `hotfix`, `performance`,
  `data-integrity`.
- **Fix Version**: Indicates release scope. A patch version suggests a targeted fix;
  a minor/major version suggests broader changes.
- **Linked Issues**: Follow `blocks`, `is blocked by`, `relates to`, and `is caused
  by` links to understand the dependency chain.
- **Description keywords**: Look for mentions of specific tables, APIs, services,
  config keys, or feature flags.

### From Diffs / PRs

Extract these structural signals:

- **Changed files**: Group by directory to identify affected layers (API, service,
  repository, model, UI, config, migration, test).
- **Changed functions/methods**: Identify the specific entry points that changed.
- **Added vs. removed vs. modified lines**: Additions suggest new functionality;
  removals suggest deprecation or replacement; modifications suggest behavior change.
- **File types**: `.sql` or migration files signal schema changes. `.env`, `.yaml`,
  `.json` config files signal environment changes. Test files changing alongside
  source files is a positive coverage signal.
- **Import changes**: New imports indicate new dependencies; removed imports indicate
  decoupling.

### From Free-Text

Extract these semantic signals:

- **Module/component names**: Any noun that maps to a known module, service, or
  component.
- **Action verbs**: "added", "removed", "changed", "migrated", "refactored",
  "replaced" indicate the type of change.
- **Integration mentions**: References to external systems, APIs, databases, or
  third-party services.
- **Scope indicators**: "across the app", "in the billing module", "on the admin
  page" help bound the blast radius.

## 3. Dependency Tracing

For each directly affected area, trace one level in each direction:

### Upstream (who calls this?)

- What controllers, services, or scheduled jobs invoke the changed code?
- What API endpoints route to the changed handler?
- What UI components submit data to the changed backend?

### Downstream (what does this call?)

- What databases, caches, or external services does the changed code write to?
- What events or messages does the changed code publish?
- What other services consume the output of the changed code?

### Shared Resources

- Does the change touch a shared config file, feature flag, or environment variable?
- Does the change modify a database table used by multiple services?
- Does the change alter a shared library, utility function, or base class?

### Cross-Cutting Concerns

Flag if the change touches any of these patterns, as they amplify blast radius:
- Authentication / authorization
- Logging / audit trails
- Error handling / exception mapping
- Caching layers
- Rate limiting / throttling
- Data validation / sanitization

## 4. Risk Classification Framework

### Base Risk Assignment

Assign a base risk level to each affected area using these criteria:

- **Critical**: Handles money, auth tokens, PII, compliance data, or security
  boundaries. A failure here causes data loss, financial impact, or security breach.
- **High**: Core user-facing workflow. A failure here blocks a primary user journey
  or breaks an API contract that external consumers depend on.
- **Medium**: Non-critical feature, internal tooling, or UI element with limited
  scope. A failure here degrades experience but does not block core workflows.
- **Low**: Documentation, logging text, cosmetic styling, non-functional config.
  A failure here is visible but has no functional impact.

### Risk Escalation Rules

After base assignment, apply escalation modifiers:

1. **Database migration present**: Escalate +1 level. Schema changes are irreversible
   in production and affect all consumers of that table.
2. **API contract change**: Escalate +1 level. External consumers may break silently.
3. **Multiple unrelated modules affected**: Escalate +1 level. Cross-module changes
   are harder to test comprehensively.
4. **Shared resource modified**: Escalate +1 level. Config, env vars, and shared
   libraries have unbounded blast radius.
5. **Rollback of a previous change**: Do not escalate, but flag for smoke
   verification to confirm the rollback is clean.

Risk never escalates above Critical.

## 5. Test Selection Strategy

### With a Project Test Map

When `references/project-test-map.md` is available:

1. For each affected area, look up the mapped test cases (Jira test IDs and/or
   automated test tags/folders).
2. Prioritize by risk level: Critical area tests run first, then High, Medium, Low.
3. Include smoke tests for adjacent (non-affected) modules to catch unexpected
   side effects.
4. For automated suites, identify the specific tags, folders, or pipeline names.

### Without a Project Test Map

When no project-specific mapping exists:

1. List affected areas with risk levels.
2. Describe the type of testing needed per area (unit, integration, E2E, manual
   exploratory) without naming specific test cases.
3. Explicitly state: "No project test inventory is loaded. Provide your test catalog
   or fill in the project-test-map template to get specific test recommendations."
4. **NEVER fabricate test IDs, test case names, or suite names.**

## 6. Coverage Gap Identification

A coverage gap exists when:

- An affected area has no mapped tests (manual or automated).
- A new code path was introduced (e.g., a new conditional branch, a new notification
  channel) with no corresponding tests.
- An integration point changed but no integration or contract test covers it.
- A config change affects behavior but no test validates the new config value.

For each gap, document:
1. The area and why it is affected.
2. The risk introduced by the gap.
3. The type of test that would close it.

## 7. Regression Scope Decision Matrix

Aggregate the risk levels across all affected areas and use the highest-risk area
to anchor the decision:

| Highest Risk Present | Number of Areas | Recommended Scope |
|----------------------|-----------------|-------------------|
| Critical | Any | Full regression |
| High | 3+ | Full regression |
| High | 1-2 | Targeted regression (affected modules + smoke for adjacent) |
| Medium | 3+ | Sanity + targeted |
| Medium | 1-2 | Sanity |
| Low | Any | Smoke |

Modifiers:
- If the change is a hotfix under time pressure, note the tradeoff between speed
  and coverage explicitly.
- If automated suites exist, recommend running them in full regardless (they are
  cheap); reserve scope decisions for manual testing effort.
