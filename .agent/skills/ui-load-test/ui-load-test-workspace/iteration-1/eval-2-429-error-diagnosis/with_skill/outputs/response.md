# Diagnosing Your 12% Failure Rate and 429 Errors

## What's Happening

A 12% HTTP failure rate is well above the 5% threshold that indicates a healthy load test. The fact that most failures are **429 (Too Many Requests)** on `/api/v1/properties/vector/llm-test` tells a clear story: you are hitting the rate limit on the AI/LLM endpoint.

The `/api/v1/properties/vector/llm-test` endpoint is an AI-powered vector search endpoint. These endpoints typically have strict rate limits imposed by the backend or the upstream LLM provider. When your k6 virtual users send requests faster than the rate limit allows, the server responds with 429 status codes telling you to slow down.

This is not a bug in your test or in the backend — it is the rate limiter doing its job. The question is how to tune your test to stay within acceptable limits, or whether the rate limit itself needs adjustment for your target load profile.

## How to Confirm

1. Open the latest HTML report:
   ```powershell
   Invoke-Item (Get-ChildItem reports\search\*_report.html | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
   ```

2. In the Failure Diagnostics (red section), look for the `(429, /api/v1/properties/vector/llm-test)` group. Expand the request/response payloads to see if the response includes a `Retry-After` header or rate-limit details.

3. Also check `reports/<flow>/*_failures.json` for patterns — whether 429s start at a specific point (hitting a rate-limit window) or are evenly distributed (sustained over-limit load).

## How to Fix It

### Option 1: Increase Sleep Between Iterations (Easiest)

Recompile with a higher sleep value:
```powershell
node peco_smart_compiler_v1.js
```
When prompted for "Sleep between iterations," try **10 seconds** instead of 2. This alone reduces request rate by roughly 5x.

### Option 2: Reduce Virtual Users (VUs)

If running 10 VUs, cut to 3-5. This proportionally reduces request rate. Combine with longer sleep for maximum effect.

### Option 3: Use the Smoke Query Pool During Tuning

```powershell
Copy-Item queries-smoke.json queries.json -Force
```
5 queries instead of 100 keeps costs down while you iterate on settings.

### Option 4: Use Shorter Durations

Try 2-3 minute runs instead of 15 minutes to validate new settings before a full run.

### Option 5: Request a Rate Limit Increase (If Needed)

If your target load profile genuinely requires more throughput than the rate limit allows, the 429s are telling you the system cannot handle that load. Document the rate limit, share the report with the backend/infrastructure team, and discuss whether the limit reflects a real capacity constraint.

## Recommended Action Plan

1. Recompile with `node peco_smart_compiler_v1.js` using **3 VUs**, **10s sleep**, **2m duration**
2. Use smoke pool: `Copy-Item queries-smoke.json queries.json -Force`
3. Run the test: `.\run-search.ps1`
4. Check the report — failure rate should drop well below 5%
5. Gradually increase VUs and decrease sleep until you find the threshold where 429s begin
6. That threshold is your current system's effective concurrency limit for the LLM endpoint

## Cost Reminder

The `/api/v1/properties/vector/llm-test` endpoint is an AI endpoint that costs real money per request. While iterating on rate-limit tuning, keep durations short and use the smoke pool. Always target non-production environments unless explicitly approved.
