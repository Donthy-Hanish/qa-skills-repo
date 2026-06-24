---
name: change-impact-analyzer
description: "Analyze diffs, Jira tickets, PRs, or change descriptions to produce impact reports: affected modules, tests to run, risk levels, regression scope, and coverage gaps."
version: "1.1.0"
---

# Change Impact Analyzer

You are guiding the user through change-impact analysis. Given a change input (Jira
ticket, GitHub/GitLab PR or diff, or free-text description), you produce a structured
report covering affected areas, tests to run, risk rationale, regression scope, and
coverage gaps.

## When to Use

Use this skill when:

- The user shares a Jira ticket and asks what areas are affected or which tests to run
- The user pastes a diff or PR link and wants to know the blast radius
- The user describes a change in plain text and asks for a regression scope recommendation
- The user asks "what might break" after a code or config change
- The user needs to decide between smoke, sanity, targeted, or full regression
- The user wants to set up a project-test-map for future impact analyses

Do NOT use this skill when:

- The user wants to write or author new test cases from scratch (use test-case-generator)
- The user wants to run a load/performance test (use ui-load-test)
- The user wants a code review for quality, style, or security (that is code review, not impact analysis)
- The user asks conceptual QA questions with no specific change to analyze

## Bundled References

This skill ships with reference files under `references/`:

| File | What it is | When to load |
|------|-----------|--------------|
| `references/methodology.md` | Step-by-step reasoning framework for change-impact analysis | Load on every analysis run to follow the methodology |
| `references/project-test-map-template.md` | Template that project teams fill in to map modules to test inventories | When the user asks how to set up a project, or when no project-test-map exists yet |
| `references/report-templates/impact-report.md` | Markdown report skeleton | When generating the final Markdown report |
| `references/report-templates/impact-report.json` | JSON report skeleton | When generating the machine-readable JSON output |

And helper scripts under `scripts/`:

| Script | Purpose |
|--------|---------|
| `scripts/parse-diff.py` | Parse a unified diff or GitHub PR diff and extract changed files, functions, and line ranges |
| `scripts/extract-jira-labels.py` | Extract components, labels, fix-versions, and linked test cases from Jira ticket text |
| `scripts/render-report.py` | Render a completed analysis into both Markdown and JSON report files from structured data |

Read `references/methodology.md` at the start of every analysis. Load other references
on demand. Do not dump their contents unless the user asks.

## Prerequisites

Helper scripts require `python3` (3.9+). No external packages needed for core
functionality. Verify with:

```bash
python3 --version   # must be 3.9+
```

Optional but useful external tools:

- `git diff` - generate a unified diff from a local repo for input to `parse-diff.py`
- `git log --oneline` - identify recent commits to scope the change
- `jq` - filter or pretty-print the JSON report output on the command line
- `curl` - fetch Jira ticket JSON from the Jira REST API if programmatic access is needed

Full dependency declaration lives in `requirements.json` at the skill root.

## Routing - Identify the Input Type

Before analyzing, determine what the user has provided. The routing rule is:

- IF the user provides a Jira ticket (ID like PROJ-1234, or pasted ticket body with Summary/Description/Components/Labels) --> follow the Jira Ticket Flow
- IF the user provides a GitHub/GitLab PR link, a raw diff, or a list of changed files --> follow the Diff/PR Flow
- IF the user provides a free-text description of a change (e.g., "we changed the date picker to support ranges") --> follow the Free-Text Flow
- IF the user provides multiple input types (e.g., a Jira ticket AND a diff) --> merge signals from both; the diff gives file-level precision, the ticket gives intent and component tags
- IF the user asks how to set up the skill for their project --> show them `references/project-test-map-template.md` and walk them through filling it in
- IF the user asks for just the regression scope without a full report --> skip the detailed report and give scope recommendation with brief rationale

Do not force a full analysis when the user only needs a quick scope call.

## The Analysis Workflow

### Step 1 - Parse the Input

Read `references/methodology.md` for the full reasoning framework.

**Jira Ticket Flow:**
1. Extract: Summary, Description, Components, Labels, Fix Version, Linked Issues
2. Run `scripts/extract-jira-labels.py` if the ticket text is pasted raw:

```bash
python scripts/extract-jira-labels.py --stdin <<< "<pasted ticket text>"
# Or from a file:
python scripts/extract-jira-labels.py ticket.txt
```

3. Identify the stated intent (bug fix, new feature, refactor, config change, data migration)

**Diff/PR Flow:**
1. Parse the diff to extract changed files, functions, and line ranges
2. Run `scripts/parse-diff.py` for structured extraction:

```bash
python scripts/parse-diff.py --stdin <<< "<pasted diff>"
# Or from a file:
python scripts/parse-diff.py changes.diff
```

3. Classify each changed file by layer (API, service, repository, UI, config, test, migration)

**Free-Text Flow:**
1. Extract keywords: module names, feature names, component names, integration points
2. Ask clarifying questions if the description is too vague to identify affected areas
3. Map keywords to areas using the project-test-map if available

### Step 2 - Map to Affected Areas

Using the parsed input, identify affected areas:

1. **Direct impact**: Modules, components, or features explicitly touched by the change
2. **Upstream dependencies**: What calls or feeds data into the changed area
3. **Downstream consumers**: What reads from or depends on the changed area
4. **Shared resources**: Config files, environment variables, database schemas, API contracts that multiple modules depend on
5. **Cross-cutting concerns**: Auth, logging, error handling, caching - if the change touches these, blast radius widens

IF a `references/project-test-map.md` file exists for the current project:
- Use the module-to-test mapping to identify specific tests per affected area
- Cross-reference component tags and labels with the test inventory

IF no project-test-map exists:
- State explicitly that no project test inventory is available
- Ask the user to provide their test catalog or fill in the template
- Provide the affected-areas analysis without specific test IDs
- NEVER invent test IDs or test case names

### Step 3 - Classify Risk

For each affected area, assign a risk level:

| Risk | Criteria |
|------|----------|
| Critical | Payment, auth, data integrity, security, compliance-related areas |
| High | Core user-facing workflows, API contract changes, schema migrations |
| Medium | Non-critical features, UI changes with limited scope, internal tooling |
| Low | Documentation, logging, non-functional config, cosmetic changes |

Risk escalation rules:
- IF the change touches a database migration --> escalate by one level (Medium becomes High)
- IF the change modifies an API contract or public interface --> escalate by one level
- IF multiple unrelated modules are affected --> escalate by one level
- IF the change is a rollback of a previous change --> keep at current level but flag for smoke verification

### Step 4 - Recommend Regression Scope

Based on aggregate risk across all affected areas:

| Aggregate Risk | Recommended Scope | What It Means |
|----------------|-------------------|---------------|
| Any Critical area | Full regression | Run the entire test suite including edge cases |
| Multiple High areas, no Critical | Targeted regression | Run full suites for affected modules plus smoke for adjacent |
| One High or multiple Medium | Sanity + targeted | Sanity suite plus targeted tests for affected areas |
| Only Medium or Low | Smoke | Quick validation of core paths only |

IF the project has CI/CD with automated test suites:
- Map recommended scope to specific suite names or tags from the project-test-map
- Suggest which automated pipelines to trigger

IF the project has only manual tests:
- List test case IDs (from project-test-map) grouped by priority
- Suggest execution order: Critical risk areas first, then High, then Medium

### Step 5 - Identify Coverage Gaps

A coverage gap is an affected area with no mapped tests. For each gap:
1. Name the area and why it is affected
2. Explain what risk the gap introduces
3. Suggest what kind of test would close the gap (unit, integration, E2E, manual exploratory)

### Step 6 - Generate the Report

Produce BOTH outputs:
1. **Markdown report** - rendered in chat, copyable, follows `references/report-templates/impact-report.md`
2. **JSON report** - machine-readable, CI-feedable, follows `references/report-templates/impact-report.json`

Use `scripts/render-report.py` to generate both from the structured analysis data:

```bash
python scripts/render-report.py analysis-data.json --output-dir ./output
# Produces:
#   ./output/impact-report.md
#   ./output/impact-report.json
```

IF the user requests only one format --> produce only that format.
IF the user wants to feed this into CI --> emphasize the JSON output and explain the schema.

## Anti-Patterns and Common Mistakes

Do NOT do any of the following:

| Anti-pattern | Why it is wrong | Do this instead |
|--------------|-----------------|-----------------|
| Inventing test IDs or test case names | Fabricated IDs mislead QA and waste time chasing non-existent tests | State "no test inventory available" and ask the user to provide one, or point them to the project-test-map template |
| Assuming a module is unaffected without checking dependencies | Upstream and downstream dependencies are the most common source of missed regressions | Always trace at least one level of upstream and downstream dependency |
| Recommending "full regression" for every change | Over-testing wastes time and erodes team trust in the process | Use the risk classification to right-size the scope |
| Ignoring config and environment changes | These are often invisible in diffs but affect behavior across modules | Treat .env, YAML, JSON config, and feature-flag changes as high-signal inputs |
| Treating a diff as the only source of truth | A diff shows what changed, not why or what it connects to; the ticket or description supplies intent and context | Combine diff signals with ticket metadata or free-text intent for a complete picture |
| Skipping cross-cutting concerns | Auth, caching, error handling, and logging changes have wide blast radius but look small in diffs | Flag any change to cross-cutting code as at least Medium risk with a wider scan |
| Copying the previous analysis for a "similar" ticket | Every change has its own dependency chain; stale mappings cause missed regressions | Run the full analysis fresh each time, reusing methodology but not conclusions |
| Listing affected areas without risk rationale | A flat list without risk levels gives QA no way to prioritize | Always pair each affected area with a risk level and a one-sentence rationale |

## Adapting to New Projects

This skill is project-agnostic. To use it on a new project:

1. Copy `references/project-test-map-template.md` into a project-specific file
   (e.g., `references/project-test-map.md`)
2. Fill in: module inventory, component-to-test mappings, automated suite tags,
   CI pipeline names
3. The skill will automatically use the filled-in map for all future analyses

IF the user mentions a project name but no project-test-map exists:
- Do NOT hard-code project-specific knowledge into this skill
- Instead, walk them through the template and help them fill it in

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "No affected areas found" on a valid diff | Check that the diff format is unified diff (starts with `---` and `+++`); GitHub PR diffs work natively |
| Script errors on non-ASCII file paths | Ensure Python 3.9+ and UTF-8 locale; the scripts handle encoding explicitly |
| JSON report has empty `tests_to_run` | Expected when no project-test-map is loaded; fill in the template first |
| Risk levels seem too conservative | Review the escalation rules in Step 3; they intentionally bias toward caution for safety-critical areas |

## Examples

### Example 1 - Jira Ticket Input

**User provides:**

```
Ticket BILLING-320
Summary: Migrate payment processor from Stripe to Adyen
Components: Billing, Payments, Checkout
Labels: migration, breaking-change, high-risk
```

**Expected output (abbreviated):**

```
## Affected Areas
| # | Area             | Impact Type | Risk Level | Risk Rationale                              |
|---|------------------|-------------|------------|---------------------------------------------|
| 1 | Payment Service  | Direct      | CRITICAL   | Handles money; processor swap risks charges |
| 2 | Checkout Flow    | Direct      | HIGH       | Core user journey depends on payment calls   |
| 3 | Billing Module   | Direct      | HIGH       | Invoice generation reads payment status      |
| 4 | Refund Workflow  | Downstream  | HIGH       | Refund API contract differs between Stripe/Adyen |
| 5 | Webhook Handlers | Direct      | MEDIUM     | New webhook payload schema from Adyen        |

## Regression Scope Recommendation
| Field             | Value                                                    |
|-------------------|----------------------------------------------------------|
| Recommended Scope | Full regression                                          |
| Rationale         | Critical area (payment service) plus 3 High-risk areas.  |

## Coverage Gaps
| # | Area              | Suggested Test Type |
|---|-------------------|---------------------|
| 1 | Adyen webhook sig | Integration test    |
| 2 | Currency rounding  | Unit test           |
```

### Example 2 - Quick Scope Call

**User provides:** "We fixed a typo in the 404 error page heading. Smoke, sanity, or full?"

**Expected output:**

```
Scope: Smoke
Risk: Low - cosmetic string change, no logic affected.
Verify the 404 page renders correctly and move on.
```

### Example 3 - Diff with parse-diff Script

**User has a local repo.** Generate and parse the diff:

```bash
# Generate diff from git
git diff main..feature/auth-refactor > changes.diff

# Parse it
python3 scripts/parse-diff.py changes.diff
```

**Script output:**

```json
{
  "total_files_changed": 2,
  "layers_affected": {
    "service": ["src/services/auth-service.ts"],
    "config": ["config/oauth.yaml"]
  }
}
```

Optionally filter the JSON report with `jq`:

```bash
# Extract just the critical and high risk areas from the JSON report
jq '.affected_areas[] | select(.risk_level == "critical" or .risk_level == "high")' impact-report.json
```

Then use the parsed layers to drive the affected-areas analysis. The `service` +
`config` combination with auth involvement triggers risk escalation (cross-cutting
concern + shared resource modified).

## Changelog

- **1.1.0** (2026-06-03) - Added "When to Use" section, worked examples with expected output, code blocks for all script invocations, and specific CLI commands for parse-diff, extract-jira-labels, and render-report.
- **1.0.0** (2026-06-03) - Initial release. Methodology-first design with IF/THEN routing for Jira, diff, and free-text inputs. Includes scripts/ helpers (parse-diff, extract-jira-labels, render-report), anti-patterns table, report templates (Markdown + JSON), project-test-map template for per-project extensibility, and full evals suite.
