"""
API Contract Test Runner
========================
Configure the section below, then run: python contract_runner.py

Requires: pip install requests urllib3
"""

import json
import requests
import concurrent.futures
import urllib3
import re
import sys
import time
import csv
import os
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =====================================================================
# CONFIGURATION — edit these values for your environment
# =====================================================================
BASE_URL = 'https://your-api-stage.company.com'
SWAGGER_FILE = 'swagger.json'
TEST_DATA_FILE = 'test_data.csv'
MAX_WORKERS = 5
SSL_VERIFY = False   # set True if the environment has a valid public certificate

# Auth: choose a pattern from references/auth-patterns.md and implement below.
# The authenticate() function must return a dict of headers to add to every request.
def authenticate():
    raise NotImplementedError(
        "Configure authentication before running. "
        "See references/auth-patterns.md for patterns."
    )
# =====================================================================


def resolve_path(path):
    return re.sub(r'\{[^}]+\}', '1', path)


def resolve_ref(ref_str, swagger_data):
    parts = ref_str.lstrip('#/').split('/')
    curr = swagger_data
    for p in parts:
        curr = curr.get(p, {})
    return curr


def build_mock_from_schema(schema, swagger_data):
    if not schema:
        return None
    if '$ref' in schema:
        return build_mock_from_schema(resolve_ref(schema['$ref'], swagger_data), swagger_data)

    schema_type = schema.get('type')
    if not schema_type:
        if 'properties' in schema:
            schema_type = 'object'
        elif 'items' in schema:
            schema_type = 'array'

    if schema_type == 'string':
        return 'test_string'
    elif schema_type in ('integer', 'number'):
        return 1
    elif schema_type == 'boolean':
        return True
    elif schema_type == 'array':
        item_schema = schema.get('items', {})
        val = build_mock_from_schema(item_schema, swagger_data) if item_schema else None
        return [val] if val is not None else []
    elif schema_type == 'object':
        props = schema.get('properties', {})
        return {k: v for k, prop in props.items()
                if (v := build_mock_from_schema(prop, swagger_data)) is not None}
    return None


def generate_mock_payload(path, swagger_data):
    try:
        post_op = swagger_data.get('paths', {}).get(path, {}).get('post', {})
        content = post_op.get('requestBody', {}).get('content', {})
        json_content = (content.get('application/json') or
                        content.get('application/json-patch+json') or
                        content.get('text/json') or
                        content.get('application/*+json'))
        if json_content and 'schema' in json_content:
            mock = build_mock_from_schema(json_content['schema'], swagger_data)
            if mock is not None:
                return mock
        for param in post_op.get('parameters', []):
            if param.get('in') == 'body' and 'schema' in param:
                mock = build_mock_from_schema(param['schema'], swagger_data)
                if mock is not None:
                    return mock
    except Exception:
        pass
    return {}


def get_response_schema(path, method, status_code, swagger_data):
    try:
        operation = swagger_data.get('paths', {}).get(path, {}).get(method.lower(), {})
        response_def = operation.get('responses', {}).get(str(status_code))
        if not response_def:
            return None
        content = response_def.get('content', {})
        json_content = (content.get('application/json') or
                        content.get('text/plain') or
                        content.get('text/json'))
        if json_content and 'schema' in json_content:
            return json_content['schema']
    except Exception:
        pass
    return None


def validate_against_schema(data, schema, swagger_data, path='root'):
    violations = []
    if not schema:
        return violations

    if '$ref' in schema:
        schema = resolve_ref(schema['$ref'], swagger_data)

    schema_type = schema.get('type')
    if not schema_type:
        if 'properties' in schema:
            schema_type = 'object'
        elif 'items' in schema:
            schema_type = 'array'

    if data is None:
        if not schema.get('nullable', False):
            violations.append(f"{path}: expected {schema_type or 'value'}, got null")
        return violations

    if schema_type == 'string' and not isinstance(data, str):
        violations.append(f"{path}: expected string, got {type(data).__name__}")
    elif schema_type in ('integer', 'number') and (not isinstance(data, (int, float)) or isinstance(data, bool)):
        violations.append(f"{path}: expected {schema_type}, got {type(data).__name__}")
    elif schema_type == 'boolean' and not isinstance(data, bool):
        violations.append(f"{path}: expected boolean, got {type(data).__name__}")
    elif schema_type == 'array':
        if not isinstance(data, list):
            violations.append(f"{path}: expected array, got {type(data).__name__}")
        else:
            item_schema = schema.get('items', {})
            for i, item in enumerate(data[:3]):
                violations.extend(validate_against_schema(item, item_schema, swagger_data, f"{path}[{i}]"))
    elif schema_type == 'object':
        if not isinstance(data, dict):
            violations.append(f"{path}: expected object, got {type(data).__name__}")
        else:
            properties = schema.get('properties', {})
            for field in schema.get('required', []):
                if field not in data:
                    violations.append(f"{path}.{field}: required field missing")
            if schema.get('additionalProperties') is False:
                for key in data:
                    if key not in properties:
                        violations.append(f"{path}.{key}: undocumented field (contract breach)")
            for prop_name, prop_schema in properties.items():
                if prop_name in data:
                    violations.extend(validate_against_schema(
                        data[prop_name], prop_schema, swagger_data, f"{path}.{prop_name}"
                    ))
    return violations


def load_test_data(csv_file):
    if not os.path.exists(csv_file):
        print(f"No '{csv_file}' found — running Swagger auto-mocks only.")
        return []
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))
        print(f"Loaded {len(rows)} QA scenarios from {csv_file}")
        return rows
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return []


def ping_endpoint(session, task, swagger_data):
    start = time.time()
    method = task['method']
    original_path = task['endpoint']
    resolved_url = f"{BASE_URL.rstrip('/')}/{resolve_path(original_path).lstrip('/')}"
    payload = task['payload']
    expected_status = str(task['expected_status'])
    scenario = task['scenario']
    source = task['source']

    try:
        if method.lower() == 'get':
            response = session.get(resolved_url, timeout=30)
        elif method.lower() == 'post':
            response = session.post(resolved_url, json=payload, timeout=30)
        else:
            return (original_path, method, scenario, source, "ERROR", "InvalidMethod",
                    int((time.time() - start) * 1000), [])

        status = str(response.status_code)
        latency_ms = int((time.time() - start) * 1000)

        pass_fail = "FAIL"
        if status == expected_status:
            pass_fail = "PASS"
        elif source == 'Swagger' and status in ('200', '201', '202'):
            pass_fail = "PASS"

        contract_violations = []
        body_text = response.text.strip()
        if pass_fail == "PASS" and body_text:
            try:
                body_json = json.loads(body_text)
                expected_schema = get_response_schema(original_path, method, int(status), swagger_data)
                if expected_schema:
                    contract_violations = validate_against_schema(body_json, expected_schema, swagger_data)
            except (json.JSONDecodeError, ValueError):
                pass

        if contract_violations:
            pass_fail = "CONTRACT FAIL"

        return (original_path, method, scenario, source, status, pass_fail, latency_ms, contract_violations)

    except requests.exceptions.Timeout:
        return (original_path, method, scenario, source, "TIMEOUT", "TimeoutError",
                int((time.time() - start) * 1000), [])
    except Exception as e:
        return (original_path, method, scenario, source, "ERROR", type(e).__name__,
                int((time.time() - start) * 1000), [])


def main():
    print(f"Loading Swagger schema from: {SWAGGER_FILE}")
    try:
        with open(SWAGGER_FILE, 'r', encoding='utf-8') as f:
            swagger_data = json.load(f)
    except Exception as e:
        print(f"Error loading swagger: {e}")
        return

    paths = swagger_data.get('paths', {})
    swagger_endpoints = [
        (method.upper(), path)
        for path, path_item in paths.items()
        if isinstance(path_item, dict)
        for method in ['get', 'post']
        if method in path_item
    ]

    if not swagger_endpoints:
        print("No GET or POST endpoints found in spec.")
        return

    print("\n[Auth] Authenticating...")
    auth_headers = authenticate()
    print("[Auth] Done.\n")

    execution_plan = []
    covered = set()

    csv_scenarios = load_test_data(TEST_DATA_FILE)
    for row in csv_scenarios:
        ep = row.get('Endpoint', '').strip()
        meth = row.get('Method', '').strip().upper()
        if not ep or not meth:
            continue
        try:
            payload = json.loads(row.get('Payload', '{}'))
        except Exception:
            payload = {}
        covered.add(f"{meth}|{ep}")
        execution_plan.append({
            'endpoint': ep, 'method': meth, 'payload': payload,
            'expected_status': row.get('Expected Status', '200').strip(),
            'scenario': row.get('Scenario', 'QA Custom Test').strip(),
            'source': 'CSV'
        })

    for method, path in swagger_endpoints:
        if f"{method}|{path}" not in covered:
            execution_plan.append({
                'endpoint': path, 'method': method,
                'payload': generate_mock_payload(path, swagger_data),
                'expected_status': '200',
                'scenario': 'Auto-Generated Smoke Test',
                'source': 'Swagger'
            })

    session = requests.Session()
    session.verify = SSL_VERIFY
    session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})
    session.headers.update(auth_headers)

    print(f"Running {len(execution_plan)} tests ({len(csv_scenarios)} CSV + "
          f"{len(execution_plan) - len(csv_scenarios)} Swagger auto)...\n")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(ping_endpoint, session, task, swagger_data)
                   for task in execution_plan]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    print(f"\n{'Src':<7} | {'Method':<6} | {'Status':<6} | {'Result':<14} | "
          f"{'Viol.':<6} | {'Scenario':<28} | Endpoint")
    print("-" * 130)

    csv_data = []
    pass_count = contract_fail_count = fail_count = 0
    for original_path, method, scenario, source, status, pass_fail, latency, violations in results:
        if pass_fail == "PASS":
            pass_count += 1
        elif pass_fail == "CONTRACT FAIL":
            contract_fail_count += 1
        else:
            fail_count += 1
        display = scenario[:25] + "..." if len(scenario) > 28 else scenario
        viol_count = str(len(violations)) if violations else "-"
        print(f"{source:<7} | {method:<6} | {str(status):<6} | {pass_fail:<14} | "
              f"{viol_count:<6} | {display:<28} | {original_path}")
        csv_data.append({
            'Source': source, 'Scenario': scenario, 'Endpoint': original_path,
            'Method': method, 'Status Code': str(status), 'Pass/Fail': pass_fail,
            'Latency (ms)': latency,
            'Contract Violations': '; '.join(violations) if violations else ''
        })

    print("-" * 130)
    print(f"Summary: {pass_count} PASS | {contract_fail_count} CONTRACT FAIL | "
          f"{fail_count} FAIL | {len(results)} total")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'contract_results_{timestamp}.csv'
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Source', 'Scenario', 'Endpoint', 'Method',
                'Status Code', 'Pass/Fail', 'Latency (ms)', 'Contract Violations'
            ])
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"\nReport saved: {csv_filename}")
    except Exception as e:
        print(f"\nFailed to write report: {e}")


if __name__ == '__main__':
    main()
