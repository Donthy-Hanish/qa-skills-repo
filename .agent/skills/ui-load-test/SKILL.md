---
name: ui-load-test
description: "Run PECO AI-search load tests end-to-end: capture HAR files, manage query pools, compile HAR into k6 scripts, execute and analyze results. Triggers on k6, HAR, load/stress testing, VU config."
---

# UI Load Test

You are guiding the user through PECO's load-testing workflow. The project lives at
`C:\Users\costrategix\PycharmProjects\PECO-Load-Tester`. All commands run from that
directory.

## Bundled References

This skill ships with three reference files under `references/`:

| File | What it is | When to load |
|------|-----------|--------------|
| `references/peco_smart_compiler_v1.js` | The exact compiler source the workflow uses | When the user asks how the compiler auto-detects endpoints, what thresholds it sets, or wants to modify compile behavior |
| `references/queries-sample.json` | A real 100-query commercial-property pool (template for custom pools) | When the user wants to author a custom query pool and needs to see the schema and tone in context |
| `references/project-context.md` | Project-level architecture, file map, output dirs | When the user asks structural questions: where files land, what each compiler variant does, generated-script behavior |

And helper scripts under `scripts/`:

| Script | Purpose | When to run |
|---|---|---|
| `scripts/preflight.ps1` | Verify k6, node, and the project directory exist | Before first test run, or when setup errors appear |
| `scripts/switch-pool.ps1` | Switch the active `queries.json` to one of the four built-in pools | Phase 2, when changing query pools without recompile |
| `scripts/open-latest-report.ps1` | Open the most recent HTML report for a given flow | After Phase 4 completes, or when reviewing past results |

Read references on demand. Do not dump their contents unless the user asks.

## Prerequisites

Before starting, verify the user has these installed:

```powershell
node --version   # must be 18+
k6 version       # from https://k6.io
```

Playwright Chromium is needed only for HAR capture: `npx playwright install chromium`

Or run the bundled preflight check: `.\scripts\preflight.ps1`

Full dependency declaration lives in `requirements.json` at the skill root.

## Routing - Where Is the User?

There are four phases. Ask the user where they are, then jump in. The routing rule is:

- IF the user has not captured a HAR yet → start at Phase 1
- IF a HAR exists but no k6 script is generated yet → start at Phase 3
- IF a k6 script is generated but no run has happened → start at Phase 4
- IF a run has completed and the user has questions → go to "Analyzing Results"
- IF the user is switching query pools only → Phase 2 alone (no recompile)

Do not force restart from Phase 1 if they already have artifacts downstream.

## The Workflow

### Phase 1 - Capture a HAR File

The user records browser traffic from the PECO frontend:

```powershell
npx playwright open https://<peco-frontend-url>/ --save-har=peco_search.har
```

They interact with the UI (search, browse, etc.), then close the browser. The HAR
lands in the project root. Ask them for the PECO frontend URL if they don't provide one.

### Phase 2 - Select or Create a Query Pool

The k6 script randomizes queries per iteration to defeat LLM cache and simulate
realistic load. Four built-in pools exist:

| Pool file | Count | Use case |
|-----------|-------|----------|
| `queries-smoke.json` | 5 | Quick validation after compile |
| `queries-full.json` | 100 | Standard load test (lat/lng=0) |
| `queries-full-geocoded.json` | 100 | Load test with real city coordinates |
| `queries-edge-cases.json` | 10 | Regulatory/zoning stress (SCIF, HUBZone, Section 8) |

To activate a pool, either:

```powershell
# Manual
Copy-Item queries-full-geocoded.json queries.json -Force

# Or use the helper
.\scripts\switch-pool.ps1 -Pool full-geocoded
```

No recompilation needed when switching pools - just copy and re-run.

#### Creating Custom Query Pools

Refer to `references/queries-sample.json` for real-world schema and tone, then produce
a JSON array:

```json
[
  {"userQuery": "descriptive natural-language search query", "lat": 0, "lng": 0}
]
```

- `userQuery`: the search text a real user would type into the PECO chat
- `lat`/`lng`: set to 0 unless testing geolocation-aware behavior
- Save as a named variant (e.g., `queries-healthcare.json`)
- Variety in geography, property type, and complexity = realistic load

### Phase 3 - Compile HAR to k6 Script

```powershell
node peco_smart_compiler_v1.js
```

This is interactive. The compiler prompts for:
1. **HAR file path** - relative path to the `.har` file
2. **VUs (concurrent users)** - start with 3-5 for smoke, scale up for stress
3. **Execution mode** - `1` for duration-based, `2` for iteration-based
4. **Duration or iterations** - e.g., `2m`, `15m`, or `5`
5. **Sleep between iterations** - seconds; default `2`; lower = more aggressive

Auto-detected from the HAR:
- API host (most-frequent origin)
- API path prefix (`/api/v1`, etc.)
- Auth header (`X-API-Key`, `Api-Key`, `Authorization`)
- AI/LLM endpoints with cost warning

Outputs:
- `performance/peco_<flow>_smart_load.js` - the k6 test script
- `peco_postprocess.js` - failure log enricher
- `run-<flow>.ps1` - PowerShell wrapper

IF the user asks how detection works internally → open
`references/peco_smart_compiler_v1.js` and answer from source rather than guessing.

### Phase 4 - Run the Test

```powershell
.\run-search.ps1
```

(Replace `search` with the flow name derived from the HAR filename.)

The wrapper runs k6, tees stdout to a timestamped log in `logs/`, then calls the
post-processor to inject Failure Diagnostics into the HTML report.

## Analyzing Results

Reports live in `reports/<flow>/`. Open the latest with the helper:

```powershell
.\scripts\open-latest-report.ps1 -Flow search
```

### Reading the HTML Report

The report has three sections:

1. **Run Metadata banner (green)** - timestamp, VUs, iterations, request count, failure rate, p(95)
2. **k6 metrics dashboard** - latency distribution, request rate, data transfer, checks
3. **Failure Diagnostics (red)** - grouped by (endpoint, status), expandable payloads

### What to Look For

- **p(95) latency**: AI endpoints under 10s, non-AI under 2s
- **HTTP failure rate**: under 5%
- **Failure clustering**: one endpoint? one status? specific query type?
- **429 errors** → reduce VUs OR increase sleep
- **5xx errors** → backend issue; check correlation with concurrency
- **Empty 200s** → semantic failure (compiler doesn't flag); investigate manually

Each run also produces `reports/<flow>/*_failures.json` for programmatic analysis.

## Cost Control

AI/LLM endpoints cost real money. To reduce spend:
- Sleep 10s instead of 2s = ~5x fewer requests
- Shorter durations during development
- Use the smoke pool while iterating
- Non-production environments only unless explicitly approved

## Anti-Patterns and Common Mistakes

Do NOT do any of the following:

| Anti-pattern | Why it's wrong | Do this instead |
|--------------|----------------|-----------------|
| Editing the generated `performance/peco_<flow>_smart_load.js` directly | Next recompile wipes the changes | Modify `peco_smart_compiler_v1.js` (the compiler) and recompile |
| Recompiling after switching query pools | Pool is loaded at runtime via `SharedArray` from `queries.json` | Just `Copy-Item` the new pool and re-run |
| Running load tests against production without approval | Real LLM cost + risk of impacting real users | Always confirm environment; cost estimate before kicking off |
| Treating "thresholds passed" as "no failures" | Thresholds = SLOs (5% error, p95 bands); individual failures still occur | Read `failures.json` and the red Failure Diagnostics section regardless |
| Ignoring 429s and just adding more VUs | Worsens the rate-limit problem and skews results | Reduce VUs OR raise sleep; coordinate with backend on rate limits |
| Using `qgrid_smart_compiler_v15.js` for PECO | QGrid compiler handles login flows / per-VU auth; PECO doesn't need it and the output will be wrong | Use `peco_smart_compiler_v1.js` |
| Comparing runs across different query pools | Different queries = different LLM cost and latency profile; not apples-to-apples | Keep the pool constant when measuring regression |
| Skipping the cost prompt by hitting Enter blindly | Easy to spend $10+ in one mistake on a 20-VU 30-min run | Read the estimate and confirm intentionally |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `k6 not recognized` | Restart PowerShell after installing k6; or run `.\scripts\preflight.ps1` |
| Console mojibake (`Γ£à`) | Recompile - V1 sets UTF-8 encoding in the wrapper |
| `could not load JS test` | Check the generated `.js` in `performance/` at the error line |
| Failure section empty but failures happened | Check log for `__PECO_FAILURE_BEGIN__`; rerun: `node peco_postprocess.js logs\<latest>.log <flow>` |
| High error rate but "Failures captured: 0" | Backend returning 200 with empty body (semantic failure, not HTTP) |

## Compiler Variants

For deeper architectural questions, see `references/project-context.md`.

- `peco_smart_compiler_v1.js` - primary, use this
- `peco_smart_compiler_v1_new.js` - newer variant under development
- `peco_smart_compiler_v1a.js` - alternate variant
- `qgrid_smart_compiler_v15.js` - for QGrid (login-flow auth), not PECO

## Changelog

- **1.1.0** (2026-06-02) - Added scripts/ helpers (preflight, switch-pool, open-latest-report), anti-patterns table, IF/THEN routing rules, inline YAML description.
- **1.0.0** (2026-06-02) - Initial release with 4 deliverables: SKILL.md, requirements.json, trigger-eval.json, test-prompts.json. Bundled compiler source, sample query pool, and project context under references/.
