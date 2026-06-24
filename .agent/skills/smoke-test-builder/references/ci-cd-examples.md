# CI/CD Smoke Test Execution Integration Examples

This document outlines pipeline configurations for triggering the generated post-deployment smoke test suite across popular CI/CD platforms.

## 1. GitHub Actions (.github/workflows/smoke-test.yml)
Triggered when a deployment completes successfully.

```yaml
name: Deployment Smoke Test
on:
  deployment_status:
jobs:
  smoke-test:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Python & Playwright
        run: |
          pip install playwright pytest
          playwright install chromium
      - name: Run Smoke Tests
        env:
          TARGET_URL: ${{ github.event.deployment_status.target_url }}
        run: pytest test_smoke.py
```

## 2. GitLab CI/CD (.gitlab-ci.yml)
Runs post-deployment validation using newman for APIs.

```yaml
stages:
  - deploy
  - smoke-test

deploy-staging:
  stage: deploy
  script:
    - echo "Deploying application to staging..."

run-smoke-tests:
  stage: smoke-test
  image: postman/newman:latest
  script:
    - newman run api_smoke_collection.json --env-var BASE_URL=https://api.stage.company.com/v1
  needs:
    - deploy-staging
```

## 3. AWS CodePipeline (buildspec.yml)
Integrates smoke testing using python requests or curl.

```yaml
version: 0.2
phases:
  install:
    commands:
      - pip install requests
  build:
    commands:
      - echo "Running smoke tests..."
      - python -c "import requests; r=requests.get('https://stage.company.com/health'); exit(0 if r.status_code==200 else 1)"
```