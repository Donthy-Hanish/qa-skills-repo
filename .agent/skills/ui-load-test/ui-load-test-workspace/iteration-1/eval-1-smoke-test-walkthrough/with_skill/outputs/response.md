# Smoke Test Walkthrough

Great, you've got your HAR file — here's what to do next.

## Step 1 — Select the Smoke Query Pool

Since this is a quick smoke test, use the 5-query smoke pool:

```powershell
Copy-Item queries-smoke.json queries.json -Force
```

This gives you 5 varied queries that rotate per iteration, enough to validate the flow without burning time or LLM cost.

## Step 2 — Compile the HAR

```powershell
node peco_smart_compiler_v1.js
```

When prompted, enter:
- **HAR file path:** `peco_search.har`
- **Concurrent users (VUs):** `3`
- **Execution mode:** `1` (duration-based)
- **Duration:** `2m`
- **Sleep between iterations:** `2` (default is fine for smoke)

The compiler will auto-detect your API host, auth header, and flag any AI/LLM endpoints with a cost estimate. Review the estimate — at 3 VUs for 2 minutes it should be minimal.

It outputs three files:
- `performance/peco_search_smart_load.js` — the k6 script
- `peco_postprocess.js` — failure log enricher
- `run-search.ps1` — one-command wrapper

## Step 3 — Run the Test

```powershell
.\run-search.ps1
```

You'll see k6's live progress, VU start messages, and a metrics summary at the end. The post-processor runs automatically to enrich the HTML report.

## Step 4 — View the Report

```powershell
Invoke-Item (Get-ChildItem reports\search\*_report.html | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

Check:
- **Top green banner** — run metadata, failure rate, p(95) latency at a glance
- **Middle** — full k6 metrics dashboard
- **Bottom** — Failure Diagnostics (red section if any failures; green "No failed requests" if clean)

If everything looks good, you're ready to scale up: switch to `queries-full-geocoded.json`, increase VUs, and run longer durations.
