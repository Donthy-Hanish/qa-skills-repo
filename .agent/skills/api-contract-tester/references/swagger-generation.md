# Swagger / OpenAPI Generation Guide

## Purpose

This reference explains how Swagger/OpenAPI becomes available for the API Contract Certification Skill. The skill can work with either a specification-first flow, where the contract is created before implementation, or a code-first flow, where the contract is generated from an existing or updated repository.

## Why Swagger/OpenAPI Matters

Swagger/OpenAPI acts as the source of truth for contract testing. The contract runner compares the live API response against the specification to identify mismatches such as missing required fields, wrong data types, invalid enum values, incorrect status codes, or schema structure differences.

## Supported Specification Sources

The skill can consume:

- `swagger.json`
- `openapi.json`
- `openapi.yaml`
- Swagger/OpenAPI URL
- OpenAPI 3.0 specification
- OpenAPI 3.1 specification
- Swagger 2.0 specification, if the runner supports it or it is converted to OpenAPI

## Flow A: Spec-Driven Development

In Spec-Driven Development, Swagger/OpenAPI is created first.

```text
Business / API Requirement
        ↓
Swagger / OpenAPI Contract Created
        ↓
AI Agent Generates API Code from Contract
        ↓
Application Deployed
        ↓
QA Runs Contract Tests Against Live API
```

### QA Expectation

The deployed API must behave according to the original specification. Any mismatch should be treated as a possible implementation defect, contract defect, or environment issue.

## Flow B: Code-First / Existing Repo Improvement

In a code-first or existing-repository improvement flow, Swagger/OpenAPI may be generated from the application code.

```text
Existing / Updated Repository
        ↓
Swagger/OpenAPI Generated from Code
        ↓
swagger.json or openapi.json Extracted
        ↓
Application Deployed
        ↓
QA Runs Contract Tests Against Live API
```

### QA Expectation

The generated contract should accurately represent the intended API behavior. QA should ensure that the generated contract is not blindly accepted if it misses business expectations.

## Common Ways to Generate Swagger/OpenAPI

The exact command depends on the technology stack. Use the project-specific build or runtime instructions where available.

| Stack | Common Approach |
|---|---|
| Java Spring Boot | Use Springdoc OpenAPI or Swagger annotations and access `/v3/api-docs`. |
| .NET Core / ASP.NET Core | Use Swashbuckle or NSwag and access `/swagger/v1/swagger.json`. |
| Node.js / Express | Use swagger-jsdoc, tsoa, NestJS Swagger, or OpenAPI decorators. |
| Python FastAPI | OpenAPI is usually available at `/openapi.json`. |
| Python Flask | Use Flask-RESTX, Flasgger, Connexion, or APIFlask. |
| Django REST Framework | Use drf-spectacular or drf-yasg. |
| Go | Use swaggo/swag, go-swagger, or oapi-codegen. |

## Minimum Inputs Needed by the Skill

Before running contract tests, collect:

- Swagger/OpenAPI file path or URL
- Base URL of deployed API
- Environment name, such as dev, QA, stage, or production
- Authentication pattern
- Required headers
- `test_data.csv`
- Report output path
- Test mode, such as smoke or regression

## Specification Quality Checklist

Before using the specification for certification, verify:

- All required endpoints are present
- HTTP methods are correct
- Request parameters are defined
- Request body schemas are defined where applicable
- Response schemas are defined for expected status codes
- Required fields are marked correctly
- Data types are accurate
- Enum values are complete
- Nullable behavior is represented correctly
- Error responses are documented
- Authentication requirements are defined
- Version information is clear

## Contract Source Decision

| Situation | Recommended Action |
|---|---|
| Specification exists before code | Use the original specification as the source of truth. |
| Specification generated from updated code | Review the generated specification before certification. |
| Old and new specs are available | Compare them for breaking changes before running full tests. |
| No specification exists | Generate Swagger/OpenAPI from the repo or request the API team to provide it. |
| Specification is incomplete | Mark certification as blocked or partial until the contract is corrected. |

## Important QA Caution

A generated Swagger/OpenAPI file may reflect what the code currently does, not necessarily what the business expected. For stronger QA certification, compare the generated specification with requirements, user stories, or the previously approved API contract.

## Recommended File Naming

Use clear names for traceability:

```text
openapi-dev.json
openapi-qa.json
swagger-before-ai-update.json
swagger-after-ai-update.json
openapi-v1.json
openapi-v2.json
```

## Recommended Storage

Store the contract used for certification along with the CSV report so that the test result is reproducible.

Suggested folder:

```text
reports/
├── openapi-used-for-run.json
├── contract-test-report.csv
└── certification-summary.md
```
