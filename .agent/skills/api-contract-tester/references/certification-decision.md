# Certification Decision Guide

## Purpose

This reference defines how QA should interpret API contract test results and make a certification decision for an API implementation produced through AI-assisted engineering, Spec-Driven Development, repository refactoring, or regression validation.

## Certification Goal

The goal is to decide whether the deployed live API conforms to the agreed Swagger/OpenAPI contract strongly enough to proceed to the next QA stage, release gate, or developer feedback cycle.

## Result Classifications

| Result | Meaning | Typical Action |
|---|---|---|
| CONTRACT PASS | The live API response matches the OpenAPI contract for the tested scenario. | Accept for contract scope. |
| CONTRACT FAIL | The live API response does not match the OpenAPI contract. | Review and raise defect or update contract if the contract is wrong. |
| EXECUTION FAIL | Test could not be executed due to environment, network, authentication, timeout, or configuration issue. | Fix test setup or environment and rerun. |
| SKIPPED | Test was intentionally not executed or could not run due to missing data/dependency. | Review whether coverage is still acceptable. |

## Contract Violation Categories

| Violation Type | Example | Severity Guidance |
|---|---|---|
| Missing Required Field | Contract requires `orderId`, response does not contain it. | High |
| Type Mismatch | Contract says `integer`, response returns `string`. | High |
| Status Code Mismatch | Expected `200`, actual `500`. | High |
| Schema Mismatch | Expected object, actual array. | High |
| Invalid Enum Value | Expected `ACTIVE`, `INACTIVE`; actual `PENDING_REVIEW`. | Medium to High |
| Unexpected Null | Field is null but contract does not allow null. | Medium to High |
| Missing Header | Required response header is missing. | Medium |
| Additional Field | Response contains a field not defined in the contract. | Low to Medium depending on consumer strictness |
| Empty Response Body | Contract expects body, API returns empty response. | High |
| Authentication Failure | Token missing, invalid, expired, or insufficient. | Execution issue unless auth behavior is under test |
| Timeout | API did not respond within configured limit. | Execution / performance observation |

## Certification Decision Categories

| Decision | Meaning | When to Use |
|---|---|---|
| CERTIFIED | Contract tests passed for the agreed scope. | No critical or high contract failures; execution coverage is acceptable. |
| CERTIFIED WITH OBSERVATIONS | Mostly passed, but minor issues or non-blocking observations exist. | Low-severity issues, additional fields, documentation mismatch, or skipped low-priority scenarios. |
| NOT CERTIFIED | Contract failures are significant enough to block acceptance. | High/critical failures, missing required fields, type mismatches, wrong status codes, broken core endpoints. |
| BLOCKED DUE TO EXECUTION CONFIGURATION | Certification cannot be completed because tests could not run properly. | Auth failure, base URL issue, missing test data, environment down, invalid Swagger file. |

## Recommended Certification Rules

Use these rules as a starting point. Teams can adjust based on project risk.

### CERTIFIED

Use when:

- All high-priority contract tests pass
- No critical endpoints have CONTRACT FAIL
- No high-severity schema violations exist
- Execution coverage is sufficient for the agreed scope
- Report is generated successfully

### CERTIFIED WITH OBSERVATIONS

Use when:

- High-priority APIs pass
- Only low-severity contract observations exist
- Some non-critical scenarios are skipped with valid justification
- Additional undocumented fields are present but do not break consumers
- Minor documentation correction is needed

### NOT CERTIFIED

Use when:

- Any critical endpoint has CONTRACT FAIL
- Required fields are missing
- Response data types are different from the contract
- Expected success status codes return errors
- Core response schema does not match the contract
- Breaking changes are detected without approval

### BLOCKED DUE TO EXECUTION CONFIGURATION

Use when:

- API environment is unavailable
- Authentication is not configured correctly
- Swagger/OpenAPI file is invalid or incomplete
- Base URL is wrong
- Required test data is missing
- Contract runner fails before meaningful validation

## Severity Guidelines

| Severity | Definition | Example |
|---|---|---|
| Critical | Blocks core API consumption or causes major integration failure. | Core endpoint returns 500 or response schema is completely different. |
| High | Breaks contract for required fields, data types, or expected status codes. | Required `id` missing; expected integer returned as string. |
| Medium | May affect consumers depending on usage. | Enum has undocumented value; nullable mismatch. |
| Low | Minor mismatch or documentation issue with low consumer impact. | Additional response field, description mismatch. |

## Certification Summary Template

```text
Certification Decision: CERTIFIED / CERTIFIED WITH OBSERVATIONS / NOT CERTIFIED / BLOCKED

Environment:
Swagger/OpenAPI Used:
Base URL:
Execution Date:
Total Tests Executed:
CONTRACT PASS:
CONTRACT FAIL:
EXECUTION FAIL:
SKIPPED:

Critical Failures:
High Failures:
Medium Failures:
Low Observations:

QA Summary:

Recommendation:
```

## CSV Report Fields Recommended for Decision-Making

The CSV report should include these columns where possible:

```csv
test_case_id,scenario_name,method,endpoint,expected_status_code,actual_status_code,contract_result,violation_type,violation_details,severity,priority,test_type,response_time_ms,environment,execution_timestamp,certification_recommendation
```

## Defect Logging Guidance

For each CONTRACT FAIL, include:

- Endpoint and method
- Environment
- Request data used
- Expected status and schema behavior
- Actual status and response behavior
- Violation type
- Severity
- Swagger/OpenAPI version used
- CSV report row reference
- Reproduction steps

## Final QA Note

Contract certification is not the same as full functional certification. A CERTIFIED result means the API conforms to the OpenAPI contract for the tested scope. It should still be combined with functional API testing, database validation, security testing, performance testing, and end-to-end workflow validation where required.
