# Supported QA Flows

## Purpose

This reference explains the QA flows supported by the API Contract Certification Skill. The skill is designed for AI-assisted engineering contexts where API implementations may be generated, updated, refactored, or regression-tested, and QA needs a fast, repeatable way to certify whether the deployed API conforms to the agreed Swagger/OpenAPI contract.

## Recommended Skill Purpose

This skill helps QA certify API implementations produced through AI-assisted engineering. It supports both Spec-Driven Development, where APIs are generated from Swagger/OpenAPI specifications, and existing-repository improvement flows, where AI agents analyze, refactor, or update code repositories. The skill validates whether the deployed live API conforms to the agreed Swagger/OpenAPI contract by running automated contract tests, identifying mismatches, and generating a CSV-based certification report.

## Supported Engineering Modes

| Mode | Description | QA Purpose |
|---|---|---|
| Spec-Driven Development | Swagger/OpenAPI is created first, then AI agents generate the API implementation from the specification. | Certify that the generated API implementation matches the original specification. |
| Existing Repository Improvement | AI agents analyze and improve an existing repository for scalability, modularity, maintainability, or code quality. | Certify that refactoring or AI-driven updates did not break the API contract. |
| API Regression Validation | Existing APIs are retested against their OpenAPI contract before or after changes. | Detect response mismatches, missing fields, type changes, and contract drift. |
| Breaking Change Detection | Old and new API specifications or implementations are compared. | Identify compatibility risks before release. |

## Flow 1: Spec-Driven Development QA Flow

```text
Business / API Requirement
        ↓
Swagger / OpenAPI Contract Created First
        ↓
AI Agent Generates API Implementation
        ↓
Application is Built and Deployed
        ↓
QA Configures Base URL, Auth, and test_data.csv
        ↓
Contract Runner Executes Live API Tests
        ↓
Live API Response Compared with OpenAPI Contract
        ↓
CONTRACT PASS / CONTRACT FAIL Classification
        ↓
CSV Test Report Generated
        ↓
QA Certification Decision
```

### When to Use

Use this flow when the API implementation is newly created from a specification using AI agents or API-first engineering practices.

### Key QA Question

Does the generated API implementation match the agreed Swagger/OpenAPI specification?

## Flow 2: Existing Repository Improvement QA Flow

```text
Existing Code Repository
        ↓
AI Agent Analyzes Repository
        ↓
AI Agent Scores Code Quality
        ↓
Scoring Parameters: Scalability, Modularity, Maintainability, Architecture Health, Code Quality
        ↓
AI Agent Refactors / Updates Repository
        ↓
Improved Score Achieved
        ↓
Swagger / OpenAPI Generated or Extracted from Updated Repo
        ↓
QA Configures Base URL, Auth, and test_data.csv
        ↓
Contract Runner Executes Live API Tests
        ↓
Live API Response Compared with OpenAPI Contract
        ↓
Contract Violations Identified
        ↓
CSV Test Report Generated
        ↓
QA Certification Decision
```

### When to Use

Use this flow when an existing API repository is modified by AI agents to improve code quality, scalability, modularity, maintainability, or architecture.

### Key QA Question

Did the AI-driven repository changes preserve the expected API contract?

## Flow 3: API Regression Validation Flow

```text
Existing API Implementation
        ↓
Swagger / OpenAPI Contract Available
        ↓
Regression Scope Selected
        ↓
Smoke / Regression test_data.csv Prepared
        ↓
Contract Runner Executes Selected Endpoints
        ↓
Actual Responses Validated Against Contract
        ↓
Pass / Fail / Execution Issues Captured
        ↓
CSV Regression Report Generated
```

### When to Use

Use this flow for release validation, sprint regression, hotfix validation, smoke checks, or CI/CD contract verification.

### Key QA Question

Are the existing APIs still contract-compliant after recent changes?

## Flow 4: Breaking Change Detection Flow

```text
Old Swagger / OpenAPI Contract
        ↓
New Swagger / OpenAPI Contract
        ↓
Compare Endpoint Paths, Methods, Status Codes, Request Schemas, and Response Schemas
        ↓
Identify Removed Fields, Changed Types, Removed Endpoints, Changed Required Fields, or Enum Changes
        ↓
Classify Breaking / Non-Breaking Changes
        ↓
Generate Compatibility Risk Summary
```

### When to Use

Use this flow when API versions are changing or when the team wants to check backward compatibility before release.

### Key QA Question

Will the new API contract break existing consumers?

## Skill Boundary

This skill focuses on contract-level certification. It validates whether the deployed API follows the Swagger/OpenAPI contract.

It does validate:

- Status codes
- Response schema
- Required fields
- Data types
- Enum values
- Nullable rules
- Response structure
- Header expectations, where defined
- Contract mismatch and contract drift

It does not fully replace:

- Functional API testing
- End-to-end business workflow testing
- Database validation
- Security testing
- Performance testing
- Exploratory testing
- Complex business rule validation unless those rules are represented in the contract

## Difference from Actual API Functional Testing

| Area | API Contract Certification | Actual API Functional Testing |
|---|---|---|
| Main Goal | Certify that the live API matches Swagger/OpenAPI. | Verify that the API performs the correct business operation. |
| Source of Truth | Swagger/OpenAPI specification. | Requirements, user stories, acceptance criteria, and business rules. |
| Best For | Fast regression, smoke validation, contract compliance, and breaking change detection. | Deep business validation and workflow correctness. |
| Validates | Schema, status codes, required fields, data types, enums, response structure. | Business logic, calculations, database updates, state changes, and end-to-end flows. |
| Output | Contract report and certification decision. | Functional test result and defect report. |

## Recommended QA Decision Usage

Use the CSV report and contract summary to decide whether the implementation is ready for further QA, ready for release, or should be rejected due to contract violations.

Recommended decision categories:

- CERTIFIED
- CERTIFIED WITH OBSERVATIONS
- NOT CERTIFIED
- BLOCKED DUE TO EXECUTION CONFIGURATION
