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

# Hide corporate SSL warnings from cluttering the terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ------------- CONFIGURATION -------------
SWAGGER_FILE = 'swagger.json'
TEST_DATA_FILE = 'test_data.csv' # PHASE 2: QA Data Source
BASE_URL = 'https://tenet-api-stage1.internal-definitywfs.com'

# --- AUTHENTICATION CONFIGURATION ---
LOGIN_URL = "https://tenet-security-api-stage1.internal-definitywfs.com/api/v1/login"
TOKEN_EXCHANGE_URL = "https://tenet-api-stage1.internal-definitywfs.com/api/v1/token/generateAuthorizationToken"
APP_KEY = "72d27932-47de-4f01-b48b-f0a926af4e3b"

LOGIN_PAYLOAD = {
    "emailAddress": "divya.ramesh+2@costrategix.com",
    "password": "Codiv@123",
    "rememberMe": False
}
# ----------------------------------------

def resolve_path(path):
    return re.sub(r'\{[^}]+\}', '1', path)

def resolve_ref(ref_str, swagger_data):
    parts = ref_str.lstrip('#/').split('/')
    curr = swagger_data
    for p in parts:
        curr = curr.get(p, {})
    return curr

def get_response_schema(path, method, status_code, swagger_data):
    """Return the Swagger schema for a given endpoint's response status code."""
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
    """Recursively validate data against a Swagger schema. Returns a list of violation strings."""
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
    elif schema_type in ('integer', 'number') and not isinstance(data, (int, float)) or (schema_type == 'integer' and isinstance(data, bool)):
        violations.append(f"{path}: expected {schema_type}, got {type(data).__name__}")
    elif schema_type == 'boolean' and not isinstance(data, bool):
        violations.append(f"{path}: expected boolean, got {type(data).__name__}")
    elif schema_type == 'array':
        if not isinstance(data, list):
            violations.append(f"{path}: expected array, got {type(data).__name__}")
        else:
            item_schema = schema.get('items', {})
            for i, item in enumerate(data[:3]):  # validate first 3 items only
                violations.extend(validate_against_schema(item, item_schema, swagger_data, f"{path}[{i}]"))
    elif schema_type == 'object':
        if not isinstance(data, dict):
            violations.append(f"{path}: expected object, got {type(data).__name__}")
        else:
            properties = schema.get('properties', {})
            required_fields = schema.get('required', [])

            for field in required_fields:
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

def build_mock_from_schema(schema, swagger_data):
    if not schema:
        return None
    if '$ref' in schema:
        resolved = resolve_ref(schema['$ref'], swagger_data)
        return build_mock_from_schema(resolved, swagger_data)

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
        if item_schema:
            val = build_mock_from_schema(item_schema, swagger_data)
            return [val] if val is not None else []
        return []
    elif schema_type == 'object':
        props = schema.get('properties', {})
        mock_obj = {}
        for prop_name, prop_schema in props.items():
            mock_val = build_mock_from_schema(prop_schema, swagger_data)
            if mock_val is not None:
                mock_obj[prop_name] = mock_val
        return mock_obj
    return None

def generate_mock_payload(path, swagger_data):
    try:
        path_item = swagger_data.get('paths', {}).get(path, {})
        post_operation = path_item.get('post', {})
        request_body = post_operation.get('requestBody', {})
        content = request_body.get('content', {})
        
        json_content = content.get('application/json') or \
                       content.get('application/json-patch+json') or \
                       content.get('text/json') or \
                       content.get('application/*+json')
                       
        if json_content and 'schema' in json_content:
            mock_data = build_mock_from_schema(json_content['schema'], swagger_data)
            if mock_data is not None:
                return mock_data
                
        parameters = post_operation.get('parameters', [])
        for param in parameters:
            if param.get('in') == 'body' and 'schema' in param:
                mock_data = build_mock_from_schema(param['schema'], swagger_data)
                if mock_data is not None:
                    return mock_data
    except Exception:
        pass
    return {}

# --- PHASE 2: CSV LOADER ---
def load_test_data(csv_file):
    test_data = []
    if not os.path.exists(csv_file):
        print(f"⚠️ Notice: '{csv_file}' not found. Defaulting entirely to Swagger Auto-Mocks.")
        return test_data
        
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_data.append(row)
        print(f"✅ Loaded {len(test_data)} QA scenarios from {csv_file}")
    except Exception as e:
        print(f"❌ Error reading {csv_file}: {e}")
    return test_data

def ping_endpoint(session, task, swagger_data):
    start_time = time.time()
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
            return (original_path, method, scenario, source, "ERROR", "InvalidMethod", int((time.time() - start_time) * 1000), [])

        status = str(response.status_code)
        latency_ms = int((time.time() - start_time) * 1000)

        pass_fail = "FAIL"
        if status == expected_status:
            pass_fail = "PASS"
        elif source == 'Swagger' and status in ('200', '201', '202'):
            pass_fail = "PASS"

        # --- CONTRACT VALIDATION ---
        contract_violations = []
        body_text = response.text.strip()
        if body_text:
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
        return (original_path, method, scenario, source, "TIMEOUT", "TimeoutError", int((time.time() - start_time) * 1000), [])
    except Exception as e:
        error_name = str(e.__class__.__name__)
        return (original_path, method, scenario, source, "ERROR", error_name, int((time.time() - start_time) * 1000), [])

def main():
    print(f"Loading Definity swagger schema from: {SWAGGER_FILE}")
    try:
        with open(SWAGGER_FILE, 'r', encoding='utf-8') as f:
            swagger_data = json.load(f)
    except Exception as e:
        print(f"Error loading swagger: {e}")
        return

    paths = swagger_data.get('paths', {})
    endpoints_to_test = [(method.upper(), path) for path, path_item in paths.items() if isinstance(path_item, dict) for method in ['get', 'post'] if method in path_item]

    if not endpoints_to_test:
        print("No GET or POST endpoints found.")
        return

    # =====================================================================
    # PHASE 1: SYNCHRONOUS AUTHENTICATION
    # =====================================================================
    print("\n[Auth] Step 1: Authenticating to Stage 1 Login...")
    login_resp = requests.post(LOGIN_URL, json=LOGIN_PAYLOAD, headers={"application-key": APP_KEY}, verify=False)
    
    if login_resp.status_code != 200:
        print(f"❌ Login Failed! Status: {login_resp.status_code}")
        sys.exit(1)
        
    login_data = login_resp.json()
    lobby_token = login_data.get("data", {}).get("token")
    print("✅ Step 1 Successful: User Token retrieved.")

    print("[Auth] Step 2: Requesting Master Authorization Upgrade...")
    exchange_headers = {
        'authorization-token': lobby_token, 
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://tenet-stage1.internal-definitywfs.com',
        'Referer': 'https://tenet-stage1.internal-definitywfs.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
    }
    
    exchange_payload = {"tenantId": 2, "roleId": None}
    exch_resp = requests.post(TOKEN_EXCHANGE_URL, json=exchange_payload, headers=exchange_headers, verify=False)
    
    if exch_resp.status_code != 200:
        print(f"❌ Token Exchange Failed! Status: {exch_resp.status_code}")
        sys.exit(1)
        
    try:
        exchange_data = exch_resp.json()
        if isinstance(exchange_data, dict):
            if "data" in exchange_data and isinstance(exchange_data["data"], dict):
                if "authorizationToken" in exchange_data["data"]: master_token = str(exchange_data["data"]["authorizationToken"])
                elif "token" in exchange_data["data"]: master_token = str(exchange_data["data"]["token"])
                else: master_token = str(exchange_data["data"])
            elif "authorizationToken" in exchange_data: master_token = str(exchange_data["authorizationToken"])
            elif "token" in exchange_data: master_token = str(exchange_data["token"])
            else: master_token = str(exchange_data)
        else:
            master_token = str(exchange_data)
    except Exception:
        master_token = exch_resp.text.strip('"')
        
    if not master_token.startswith("eyJ"):
        print("❌ ERROR: Extracted token is not a valid JWT!")
        sys.exit(1)
        
    print("✅ Step 2 Successful: Upgraded to Master Admin Token!\n")

    # =====================================================================
    # PHASE 2: THE HYBRID EXECUTION PLANNER
    # =====================================================================
    execution_plan = []
    csv_endpoints_tracker = set()

    # 1. Load QA Scenarios from CSV
    csv_scenarios = load_test_data(TEST_DATA_FILE)
    for row in csv_scenarios:
        ep = row.get('Endpoint', '').strip()
        meth = row.get('Method', '').strip().upper()
        if not ep or not meth: continue
            
        try: payload = json.loads(row.get('Payload', '{}'))
        except: payload = {}
        
        expected = row.get('Expected Status', '200').strip()
        scenario_name = row.get('Scenario', 'QA Custom Test').strip()

        csv_endpoints_tracker.add(f"{meth}|{ep}")
        execution_plan.append({
            'endpoint': ep, 'method': meth, 'payload': payload,
            'expected_status': expected, 'scenario': scenario_name, 'source': 'CSV'
        })

    # 2. Auto-Fill the gaps using Swagger
    for method, original_path in endpoints_to_test:
        if f"{method.upper()}|{original_path}" not in csv_endpoints_tracker:
            payload = generate_mock_payload(original_path, swagger_data)
            execution_plan.append({
                'endpoint': original_path, 'method': method.upper(), 'payload': payload,
                'expected_status': '200', 'scenario': 'Auto-Generated Smoke Test', 'source': 'Swagger'
            })

    # =====================================================================
    # PHASE 3: THREAD-POOL VALIDATION ENGINE
    # =====================================================================
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'authorization-token': master_token, 
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://tenet-stage1.internal-definitywfs.com',
        'Referer': 'https://tenet-stage1.internal-definitywfs.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
    })

    print(f"\n🚀 Starting Execution Plan: {len(execution_plan)} total tests...")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(ping_endpoint, session, task, swagger_data) for task in execution_plan]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    # --- REPORTING ---
    print(f"\n{'Src':<7} | {'Method':<6} | {'Status':<6} | {'Result':<14} | {'Violations':<4} | {'Scenario':<28} | {'Endpoint'}")
    print("-" * 130)

    csv_data = []
    success_count = 0
    contract_fail_count = 0
    for original_path, method, scenario, source, status, pass_fail, latency, violations in results:
        if pass_fail == "PASS":
            success_count += 1
        if pass_fail == "CONTRACT FAIL":
            contract_fail_count += 1

        display_scenario = scenario[:25] + "..." if len(scenario) > 28 else scenario
        viol_count = str(len(violations)) if violations else "-"
        print(f"{source:<7} | {method:<6} | {str(status):<6} | {pass_fail:<14} | {viol_count:<10} | {display_scenario:<28} | {original_path}")

        csv_data.append({
            'Source': source,
            'Scenario': scenario,
            'Endpoint': original_path,
            'Method': method,
            'Status Code': str(status),
            'Pass/Fail': pass_fail,
            'Latency (ms)': latency,
            'Contract Violations': '; '.join(violations) if violations else ''
        })

    print("-" * 130)
    print(f"Summary: {success_count} PASS | {contract_fail_count} CONTRACT FAIL | {len(results) - success_count - contract_fail_count} FAIL | {len(results)} total")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'stage1_hybrid_results_{timestamp}.csv'
    
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                'Source', 'Scenario', 'Endpoint', 'Method',
                'Status Code', 'Pass/Fail', 'Latency (ms)', 'Contract Violations'
            ])
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"\nSuccessfully generated report: {csv_filename}")
    except Exception as e:
        print(f"\nFailed to write CSV: {e}")

if __name__ == '__main__':
    main()