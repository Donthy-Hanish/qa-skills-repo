# Enterprise Bug Report Templates & Formatting Guide

This guide contains the official structured templates and copy-pasteable examples for documenting UI, API, and AI/LLM-specific defects. Use these templates to ensure all bug reports achieve 100/100 quality grades.

---

## 1. UI Functional Bug Template

Designed for client-side visual, interaction, compatibility, and responsiveness defects.

### Markdown Layout
```markdown
# [BUG] [UI] [Summary of Visual/Functional failure]

## 1. Executive Summary
- **Defect Class**: UI Functional Bug
- **Priority****: [P1 Blocker / P2 Critical / P3 Major / P4 Minor / P5 Trivial]
- **Business Impact**: [Operational risk, e.g., blocks users from completing payment]

## 2. Environment Details
- **OS/Platform**: [e.g. macOS Sonoma, iOS 17.2, Windows 11]
- **Browser/Agent**: [e.g. Chrome v124.0, Safari Mobile]
- **Viewport Size**: [e.g. Desktop 1440px, Mobile 375px]
- **Environment**: [Staging / QA / Production]
- **Build/Git Commit**: [e.g. Commit `7d2f9a1` / Release `v1.1.2`]
- **Root Cause**: [Requirement / Design Error / Code Error / Test Error / Deployment Error / Configuration]

## 3. Steps to Reproduce
1. Navigate to `[URL/State Precondition]`
2. Click on `[Element Description]`
3. Type `[Value]` in `[Input Name]`
4. Click `[Submit/Action]`
5. Observe UI layout or action outcome

## 4. Expected vs Actual Behavior
- **Expected Behavior**: [What should have happened visually or behaviorally]
- **Actual Behavior**: [What actually happened, detailing visual overlap, console crash, or navigation failure]

## 5. Technical Evidence & Diagnostics
### Chrome Browser Console Logs
```
[Uncaught Traceback or client-side JavaScript error]
```

### Affected DOM / CSS Snippet (If known)
```html
<!-- HTML Snippet causing the overlap or crash -->
```

### Visual Evidence
- **Screenshots/Video Links**: [Link to files or attachment placeholders]
```

---

## 2. API Bug Template

Optimized for integration layer mismatches, protocol failures, data corruptions, and performance breaches.

### Markdown Layout
```markdown
# [BUG] [API] [Endpoint Title] [HTTP Status] [Brief discrepancy summary]

## 1. Executive Summary
- **Defect Class**: API Bug
- **Priority****: [P1 Blocker / P2 Critical / P3 Major / P4 Minor / P5 Trivial]
- **Endpoint**: `[METHOD] /api/v1/endpoint`
- **Business Impact**: [e.g., downstream UI client cannot parse list, breaking display]

## 2. Environment & Gateway Details
- **Environment**: [Staging / QA / Production]
- **Gateway Base URL**: `https://api-stage.platform.com`
- **Build/Git Version**: [e.g. Commit `9a3f2b1` / Swagger Spec v3.4]
- **Root Cause**: [Requirement / Design Error / Code Error / Test Error / Deployment Error / Configuration]

## 3. Steps to Reproduce
1. Send an HTTP request to `[Endpoint]` using `[Method]` and the specified body.
2. Check the response status and returned body payload.

## 4. Expected vs Actual Behavior
- **Expected Behavior**: HTTP status `[Expected Status]`, response body matches the contract schemas.
- **Actual Behavior**: HTTP status `[Actual Status]`, response body violates spec rules.

## 5. Technical Evidence & Diagnostics
### Ready-to-Run CURL Command
```bash
curl -X [METHOD] https://api-stage.platform.com/api/v1/endpoint \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN_PLACEHOLDER>" \
  -d '[Payload]'
```

### Request Headers & Payload
```json
// Request JSON
```

### Response Headers & Payload
```json
// Response JSON
```

### Diagnostics/Traces
```
[Backend Exception Traceback or database log if available]
```
```

---

## 3. AI / LLM Bug Template (Cognitive Anomalies)

A cutting-edge, specialized framework for reporting non-deterministic cognitive defects in generative AI, chatbots, and retrieval-augmented (RAG) engines.

### Markdown Layout
```markdown
# [BUG] [AI-LLM] [Model Name] [Anomaly Category] [Defect summary]

## 1. Executive Summary
- **Defect Class**: AI/LLM Bug
- **Model Name & Provider**: [e.g. Gemini 1.5 Pro, GPT-4o]
- **System Prompt Version**: [e.g. System Prompt v2.1-beta]
- **Temperature / Hyper-params**: [e.g. Temp 0.7, Top_P 0.9]
- **Anomaly Category**: [Hallucination / Prompt Injection / Toxicity / System Prompt Leak / Safety Filter False Positive / Format Mismatch / Drift]
- **Priority****: [P1 Blocker / P2 Critical / P3 Major / P4 Minor / P5 Trivial]
- **Root Cause**: [Requirement / Design Error / Code Error / Test Error / Deployment Error / Configuration]

## 2. Testing Constraints & Seed State
- **User Session Preconditions**: [e.g. Fresh context window, chat session history empty]
- **RAG Datastore State**: [e.g. Sync state of vectors as of 2026-06-01]

## 3. Cognitive Inputs & Context
- **User Prompt / Input Query**:
  > [The exact prompt input including special formatting]
- **System Context (If dynamic)**:
  > [Any retrieved database documents or contextual payloads passed in prompt]

## 4. Expected vs Actual Cognitive Behavior
- **Expected Cognitive Constraint**: [What guidelines the model should have followed (e.g. "Should never give financial advice", "Must return JSON strictly matching schema")]
- **Actual Model Behavior**: [The generative breakdown (e.g. hallucinated fake numbers, bypassed guardrails, returned text instead of JSON)]

## 5. Raw AI Outputs & Evidence
### Raw Model Output
```
[Insert the exact text or payload returned by the LLM]
```

### Guardrail / Safety Filter Log (If triggered)
```json
// Safety ratings returned, blocking valid inputs or failing to block toxicity
```

### Token & Performance Diagnostics
- **Prompt Tokens**: [Count]
- **Completion Tokens**: [Count]
- **Latency / Response Time**: [e.g., 8.4 seconds - SLA violation]

## 6. Business Impact & Scope Risk
- **Core Risk**: [e.g. financial exploit via hallucinated discount codes, brand damage from toxic outputs, security leak of system instructions]
- **Remediation Suggestion**: [e.g. update system prompt rules, implement a custom Pydantic JSON parser, lower temperature setting to 0.2]
```
