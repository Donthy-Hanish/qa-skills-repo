---
name: bug-reporter
description: "Transform raw observations, logs, and errors into structured bug reports. Trigger when asked to write a bug report, file a ticket, document a defect, or generate a Jira ticket."
---

## What This Skill Does

This skill transforms raw, unstructured observations (terminal stack traces, screenshots, raw HTTP dumps, cognitive chatbot hallucinations, or customer support complaints) into **highly structured, enterprise-grade bug reports**. 

These reports are optimized directly for modern software tracking systems like **Jira** , as well as AI-assisted agentic QA testing ecosystems.

It covers three core bug classes:
1. **UI Functional Bug**: Layout shifts, client-side JS crashes, navigation breaks, accessibility failures, and responsive breaks.
2. **API Bug**: Protocol contract failures, bad HTTP statuses, latency SLA breaches, schema validations, and gateway/authorization exceptions.
3. **AI/LLM-Specific Bug**: Cognitive anomalies (hallucinations, non-determinism, drift, toxicity, bias, system prompt leakage, formatting mismatch, and safety filters blocking valid requests).

---

## When to Use

### Activate this skill when the user:
- Asks to "write a bug report", "file a ticket", "report a bug", or "document a defect".
- Requests to turn a stack trace, console log, curl output, or error alert into a Jira issue.
- Shares a failure output from test runners (Robot Framework, Playwright, Jest, PyTest) and wants a structured bug report.
- Needs to document cognitive chatbot failures, LLM system prompt leaks, or hallucinations.
- Asks for guidelines on assessing Severity and Priority during defect triage.

### Do NOT activate this skill when the user:
- Asks to generate new test cases from a user story (use `test-case-generator` instead).
- Wants to analyze or debug flaky test runs in CI (use `flaky-test-and-self-healing` instead).
- Is asking for a standard code review, optimization, or rewrite of their application logic.
- Needs to configure CI/CD pipelines (Jenkins, GitHub Actions) or manage Git branches.

---

## Core Principles of Enterprise-Grade Defects

Every bug report must be:
- **Reproducible**: Clear, numbered steps beginning from a static baseline, noting prerequisites.
- **Objective**: Meticulous distinction between Severity (technical impact on systems) and Priority (business urgency for scheduling), strictly matching the [Severity-Priority Matrix](file:///C:/Users/costrategix/.gemini/antigravity-ide/brain/SkillCreatorPOC/.agents/skills/bug-reporter/references/severity-priority-matrix.md).
- **Evidential**: Supported by hard technical evidence (error stack traces, API payloads, network traces, console logs).
- **Actionable**: Contains expected vs actual values, exact environment parameters, and impact statements so developers can immediately start fixing the issue without endless clarifying questions.

---

## Decision Rules and Conditional Logic

Apply the following conditional logic when drafting defects:
- **IF** the bug/defect is a **UI Functional Bug** **THEN** require the OS, browser version, viewport width, and an attached path to screenshots/recordings.
- **IF** the bug/defect is an **API Bug** **THEN** extract and display the Endpoint URL, Request Method, Headers, Request Body, Response Status, Response Body, and provide a ready-to-run `curl` command.
- **IF** the bug/defect is an **AI/LLM Bug** **THEN** require the system prompt version, model name and temperature, user prompt input, actual model response, expected constraints, and categorization of failure (e.g. Hallucination, Promt Leak, Drift).
- **IF** the bug causes total system unavailability, core customer blocker, or security compromise **THEN** classify Priority as **Blocker (P1)** or **Critical (P2)**.
- **IF** there is a reasonable workaround available **THEN** downgrade Priority to **Major (P3)** or **Minor (P4)**.
- For all types of bugs/defects (**UI Functional Bug** or **API Bug** or **AI/LLM Bug**), then perform AI-powered root-cause suggestions and Classify Root Cause as **Requirement** or **Design Error** or **Code Error** or **Test Error** or **Deployment Error** or **Configuration**.

---

## Step-by-Step Process for QA Engineers & AI Agents

Follow this workflow to generate bug/defect reports:

### Step 1: Capture Raw Observations
Collect raw diagnostics from the environment. This includes console stack traces, network payloads, environment specifications, and screenshots.

### Step 2: Categorize the Defect Class
Classify the bug as a **UI Functional Bug**, **API Bug**, or **AI/LLM Bug** to select the correct template from [bug-report-templates.md](file:///C:/Users/costrategix/.gemini/antigravity-ide/brain/SkillCreatorPOC/.agents/skills/bug-reporter/references/bug-report-templates.md).

### Step 3: Run the Completeness Validator
Before writing, run the validator script to verify that your draft contains all mandatory fields and high-quality parameters:
```bash
python path/to/format_bug_report.py --validate path/to/draft_report.md
```

### Step 4: Output and Format the Defect
Render the final bug report in clean, copy-pasteable Markdown or Jira/ADO markup format.

---

## Output Format

All bug reports generated by this skill must follow the structured layouts defined in [bug-report-templates.md](file:///C:/Users/costrategix/.gemini/antigravity-ide/brain/SkillCreatorPOC/.agents/skills/bug-reporter/references/bug-report-templates.md). The output format should always be structured as:

```markdown
# [BUG] [Brief, Specific Title summarizing What, Where, and Under What Condition]

## 1. Executive Summary
- **Defect Class**: [UI Functional / API / AI-LLM]
- **Priority****: [P1 Blocker / P2 Critical / P3 Major / P4 Minor / P5 Trivial]
- **Target Platform**: [Jira]
- **Business Impact**: [Summarize financial, operational, or customer experience risk]

## 2. Environment Details
- **OS/Platform**: [e.g., Windows 11, iOS 17.2]
- **Browser/App Version**: [e.g., Chrome 124.0.2, Android App v3.4.1]
- **Environment**: [Stage / QA / Production]
- **Build/Git Commit**: [e.g., Commit `8f3b2a9` / Build `v1.2.4-RC2`]
- **Root Cause**: [Requirement / Design Error / Code Error / Test Error / Deployment Error / Configuration]

## 3. Steps to Reproduce
1. [Step 1 with starting precondition]
2. [Step 2]
3. [Step 3]

## 4. Expected vs Actual Behavior
- **Expected Behavior**: [What should have happened according to requirements]
- **Actual Behavior**: [What actually happened]

## 5. Technical Evidence & Diagnostics
### [Log / Console / Trace Name]
```
[Insert raw log, console trace, or schema violation traceback here]
```

## 6. Business Impact & Scope Risk
- **Core Impact**: [Details of lost revenue, blocked users, or operational load]
- **Risk Scope**: [Is this isolated to a single browser size, specific API client, or does it affect all users?]

---
*Defect report compiled by Enterprise Bug Reporter Agent*
```

---

## Examples

### Example 1: API Schema Violation (Transforming Raw Response)

**Raw Input from QA Agent:**
"I hit the `/api/v1/freelancers/search` endpoint on staging with method POST. Payload was `{"role": "Architect"}`. Got a 200 OK but the JSON returned didn't have the `licensed` boolean field which is mandatory according to Swagger, and the `experience` field was returned as a string `"5 years"` instead of a number/int. Standard says this is major because it breaks UI filtering logic."

**Structured Output:**
```markdown
# [BUG] API search endpoint returns invalid schema for freelancer details

## 1. Executive Summary
- **Defect Class**: API Bug
- **Priority**: P3 Major (Schema contract violation on core search API)
- **Target Platform**: Jira
- **Business Impact**: Prevents hiring representatives from filtering freelancers correctly, leading to matching delays.

## 2. Environment Details
- **Environment**: Stage
- **API Version**: `/api/v1/`
- **Build/Git Commit**: Build `v2.4.0-RC1`
- **Root Cause**: Code Error

## 3. Steps to Reproduce
1. Send a POST request to `/api/v1/freelancers/search` with the filter payload.
2. Observe the JSON response elements.

## 4. Expected vs Actual Behavior
- **Expected Behavior**: Response status 200 OK. Response JSON complies with Swagger schema definitions: `licensed` boolean is present, and `experience` is an integer.
- **Actual Behavior**: Response status 200 OK, but `licensed` field is entirely missing, and `experience` is returned as a string `"5 years"`.

## 5. Technical Evidence & Diagnostics
### Request Curl
```bash
curl -X POST https://staging.platform.com/api/v1/freelancers/search \
  -H "Content-Type: application/json" \
  -d '{"role": "Architect"}'
```

### Response Payload
```json
{
  "freelancers": [
    {
      "id": 402,
      "name": "Jane Doe",
      "role": "Architect",
      "experience": "5 years"
    }
  ]
}
```

## 6. Business Impact & Scope Risk
- **Core Impact**: The missing `licensed` attribute causes the frontend list screen to crash when applying licensing filters. String type on `experience` breaks sorted numeric listings.
- **Risk Scope**: Affects all search operations for hiring representatives on all web platforms.
```

---

## Pitfalls & Anti-Patterns to Avoid

- **Vague Steps to Reproduce**: Writing "Go to site and click search" instead of "Navigate to staging.platform.com/list, click the role filter dropdown, select Architect, and observe list." Always provide precise navigation states.
- **Subjective Triage (Severity Bias)**: Classifying every minor cosmetic bug as "S1 Blocker" because a stakeholder complained. Adhere strictly to the severity matrix rules.
- **Silent Assertions (Missing Traces)**: Filing an API bug report without including the raw request payload and curl command. Developers must never be forced to reproduce from thin air.
- **Platform Incompatibilities**: Creating raw markdown bugs for Jira instances that are strictly configured to accept only Jira Wiki markup format. Make sure to format outputs based on target system capabilities.

---

## Changelog & Version History

### [1.0.0] - 2026-06-01
- **Initial Release**: Launched the `bug-reporter` skill.
- **Domain Focuses**: Tailored reporting frameworks for UI, API, and highly specialized AI/LLM cognitive bugs.
- **Validator CLI**: Built `format_bug_report.py` to audit description quality and ensure standard adherence.
- **Templates**: Drafted distinct layouts and objective triage guidelines in the `references/` directory.
