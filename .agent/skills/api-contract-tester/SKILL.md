---
name: api-contract-tester
description: "Run API contract tests against any OpenAPI/Swagger-described REST API. Use this skill whenever the user wants to validate that a live API's responses match its Swagger/OpenAPI specification, run regression or smoke tests against REST endpoints, set up automated endpoint testing, check for breaking changes between API versions, interpret contract violation errors from test runs, write test scenarios in test_data.csv format, configure API authentication for automated testing, or generate a CSV test report. Trigger on phrases like 'run contract tests', 'test my API', 'validate swagger', 'check API responses', 'contract testing', 'API regression suite', or any time the user shares a swagger.json and asks to test it. Also trigger when the user is troubleshooting test results showing CONTRACT FAIL, type mismatches, or missing required fields."
---

## What This Skill Does

This skill runs **API contract tests** — automated checks that verify a live API's responses match what its OpenAPI/Swagger spec promises.

A test **passes** when the endpoint returns the expected status code AND the response body has the right shape: correct types, all required fields present, no undocumented extra fields.

The tool does three things most API testers skip:
1. **Auto-discovers** every endpoint from the Swagger spec (no need to manually list them)
2. **Validates response bodies** against the spec's schema definitions — not just status codes
3. **Merges custom QA scenarios** with auto-generated smoke tests so nothing gets missed

The output is a CSV report with per-endpoint Pass / Fail / CONTRACT FAIL results and exact violation details.

---

## When to Use

### Activate this skill when the user:
- Wants to run contract/schema tests against a REST API with an OpenAPI/Swagger spec (`swagger.json`, `openapi.json`).
- Asks to validate live API responses against their specification.
- Is troubleshooting error logs that show `CONTRACT FAIL`, type mismatches (e.g., `expected integer, got str`), or missing fields.
- Needs to build or configure the `contract_runner.py` script.
- Needs to define custom test scenarios in `test_data.csv`.
- Wants to set up automated smoke/regression testing for REST endpoints.

### Do NOT activate this skill when the user:
- Wants to write BDD/Gherkin test cases using Selenium or Playwright (use `test-case-generator` instead).
- Is debugging non-API UI/frontend browser tests.
- Is writing unit tests for backend code (e.g., using `pytest` or `unittest` directly on Python functions).
- Needs help with general network routing, database queries, or server-side deployment troubleshooting.

## Decision Rules and Conditional Logic

When preparing and running contract tests, apply the following logic:
- **IF** the API spec is provided in OpenAPI/Swagger format (e.g., `swagger.json` or `openapi.json`) **THEN** parse the spec and extract endpoints, HTTP methods, and schemas automatically.
- **IF** no spec is provided **THEN** prompt the user to provide the endpoint details, paths, and expected response payloads before generating any tests.
- **IF** the target API requires authentication (e.g., token, API key, JWT) **THEN** configure and include the auth header setup in the test scaffolding (e.g., in `contract_runner.py` configuration).
- **IF** a response status code is 200/201 but validation fails **THEN** report a `CONTRACT FAIL` status code with the exact schema path that caused the mismatch.

---

## Prerequisites

Ask the user to confirm before starting:

- `swagger.json` or `openapi.json` — the API spec (often at `/swagger/v1/swagger.json` on the server)
- Python 3.x installed
- Auth credentials for the **staging/QA environment** (never run automated tests against production)
- Base URL of the target environment

Install dependencies:
```bash
pip install requests urllib3
```

The runner script lives in this skill's `scripts/contract_runner.py`. Copy it to the user's project directory alongside `swagger.json`.

---

## Step 1: Configure Authentication

Read `references/auth-patterns.md` to find the right auth pattern for the user's API, then configure the top of `contract_runner.py`.

The four most common patterns are:

- **Two-step JWT** — enterprise APIs where you login, then exchange the lobby token for a privileged one
- **Single bearer token login** — standard JWT login returning `access_token`
- **Static API key** — fixed key in a header
- **OAuth2 client credentials** — machine-to-machine token endpoint

If the user is unsure how their API authenticates, ask them to open the login request in browser DevTools (Network tab) and describe what headers/body the login call sends.

The key config block is at the top of `contract_runner.py`:
```python
BASE_URL = 'https://your-api-stage.company.com'
SWAGGER_FILE = 'swagger.json'
TEST_DATA_FILE = 'test_data.csv'
MAX_WORKERS = 5
SSL_VERIFY = False  # set True if environment has a valid public cert
```

---

## Step 2: Write Custom Test Scenarios

The engine auto-generates smoke tests for every endpoint. To add **business logic tests** — specific payloads, error cases, edge cases — create `test_data.csv`.

Read `references/test-data-format.md` for the full format guide and examples.

**CSV format:**
```
Endpoint,Method,Scenario,Expected Status,Payload
```

**Good scenario coverage per endpoint:**
| Test type | Expected Status |
|-----------|----------------|
| Happy path with full valid payload | 200 or 201 |
| Missing a required field | 400 |
| Invalid field type | 400 or 422 |
| Non-existent resource | 404 |
| Unauthenticated request | 401 |
| Duplicate / constraint violation | 409 |

CSV tests take priority — any endpoint+method pair covered in the CSV won't get an auto-generated test. This lets the QA team override auto-mocks with real payloads.

---

## Step 3: Run the Tests

```bash
python contract_runner.py
```

The script will:
1. Authenticate and confirm token acquisition
2. Load CSV scenarios (or report how many were found)
3. Stream live test results to the terminal
4. Print a summary line
5. Save `contract_results_[TIMESTAMP].csv`

---

## Step 4: Interpret the Results

### Result States

| Result | Meaning |
|--------|---------|
| **PASS** | Status code matched AND response body conforms to spec |
| **FAIL** | Status code didn't match the expected code |
| **CONTRACT FAIL** | Status code was correct but response body violated the schema |
| **TIMEOUT** | Endpoint didn't respond within 30s |
| **ERROR** | Network or connection error (see error name column) |

### Decoding Contract Violations

The `Contract Violations` column in the CSV contains semicolon-separated messages. Common ones:

| Violation message | Root cause | Who fixes it |
|---|---|---|
| `root.X: required field missing` | Field marked `required` in spec but absent from response | Backend developer — field must always be returned |
| `root.X: expected integer, got str` | Type mismatch | Backend JSON serializer returning wrong type |
| `root.X: undocumented field (contract breach)` | Response includes field not in spec (and spec says `additionalProperties: false`) | Update spec OR strip field from response |
| `root: expected object, got null` | Entire response body is null/empty | Check if endpoint has data to return |
| `root[0].X: expected string, got NoneType` | Null inside an array item | Nullable handling missing in backend |

### Prioritising the Fix List

1. **CONTRACT FAIL on Swagger auto-tests** → the API is breaking its own contract today
2. **FAIL on CSV tests** → known business logic is broken
3. **CONTRACT FAIL on CSV happy-path tests** → right status, wrong shape

---

## Step 5: Common Troubleshooting

**All endpoints return 401**
→ Auth is failing. Check credentials, headers, and token extraction. Print the raw auth response to find where the JWT actually lives.

**Token extraction fails ("not a valid JWT")**
→ The exchange response shape changed. Print `exch_resp.text` and trace where `eyJ...` appears in the JSON structure.

**All POST Swagger tests return 400/422**
→ Auto-generated mock payloads use placeholder values (`"test_string"`, `1`). Fields with business constraints (minimum values, enum values, FK relationships) will fail. Cover these in `test_data.csv` with real payloads.

**Too many timeouts**
→ Reduce `MAX_WORKERS` to 2-3. The staging environment may rate-limit concurrent connections.

**`data` field always shows as null violation**
→ Check if the spec has `"nullable": true` on the `data` property. The validator respects nullable — if it's not set in the spec but null is a valid API response, the spec needs updating.

---

## Extending Coverage

To cover PUT / PATCH / DELETE endpoints, extend the discovery line in `contract_runner.py`:
```python
for method in ['get', 'post', 'put', 'patch', 'delete']:
```

To test multiple environments, run the suite with different `BASE_URL` values and diff the output CSVs — new CONTRACT FAILs indicate breaking changes introduced in that environment.

To increase concurrency for large specs (200+ endpoints):
```python
MAX_WORKERS = 10  # watch for rate limiting
```

---

## Anti-Patterns and Pitfalls

Avoid the following common mistakes when writing and executing contract tests:
- **Testing only happy paths and ignoring error responses**: Do not assume error status codes (400, 401, 404, etc.) do not have schemas. Validate that error response bodies also conform to the specified error structures in the OpenAPI spec.
- **Hardcoding test data instead of parameterizing**: Avoid placing static values inside test scripts. Use `test_data.csv` to parameterize inputs and expected outputs so that environments can be switched without editing the test runner.
- **Ignoring response time assertions**: Do not neglect latency checks. Ensure endpoints respond within SLA limits (e.g., < 30 seconds), and assert timeouts when SLA is violated.
- **Not validating response schema structure**: Do not just check the HTTP status code. Checking `status == 200` alone is not a contract test; the entire payload structure must match the spec's JSON schema constraints.

---

## Changelog

- **v1.1** (2026-05-27)
  - Added "When to Use" and "Anti-Patterns and Pitfalls" sections.
  - Defined explicit "Decision Rules and Conditional Logic".
  - Updated compatibility guidelines.
- **v1.0** (2026-05-26)
  - Initial release of the `api-contract-tester` skill.
