*** Settings ***
Documentation     API test suite template for <API Feature/Endpoint>.
...               Validates request/response contracts, status codes, and payloads.
Library           RequestsLibrary
Library           Collections
Library           JSONLibrary
Variables         variables/variables.robot

Suite Setup       Create API Session
Suite Teardown    Delete All Sessions

Force Tags        api    <feature-tag>


*** Variables ***
${API_BASE_URL}       https://api.staging.example.com
${AUTH_TOKEN}         %{API_TOKEN=default_token}
${ENDPOINT}           /api/v1/<resource>


*** Test Cases ***
# --- SMOKE ---

Verify Endpoint Is Reachable
    [Documentation]    Health check — confirm the endpoint responds
    [Tags]    smoke    critical
    ${response}=    GET On Session    api    ${ENDPOINT}
    Status Should Be    200    ${response}

# --- POSITIVE ---

Create Resource With Valid Payload
    [Documentation]    POST with valid data returns 201 and correct body
    [Tags]    regression    critical    crud
    ${payload}=    Create Dictionary
    ...    name=Test Resource
    ...    type=standard
    ${response}=    POST On Session    api    ${ENDPOINT}    json=${payload}
    Status Should Be    201    ${response}
    Dictionary Should Contain Key    ${response.json()}    id
    Should Be Equal    ${response.json()}[name]    Test Resource

# --- NEGATIVE ---

Create Resource With Missing Required Field
    [Documentation]    POST without required 'name' field returns 400
    [Tags]    regression    high    validation
    ${payload}=    Create Dictionary    type=standard
    ${response}=    POST On Session    api    ${ENDPOINT}
    ...    json=${payload}    expected_status=400
    Should Contain    ${response.json()}[error]    name is required

# --- DATA-DRIVEN ---

Validate Status Codes For Various Inputs
    [Documentation]    Parameterized test for multiple input/status combinations
    [Tags]    regression    high    data-driven
    [Template]    POST And Verify Status
    # payload_key    payload_value    expected_status
    name             Valid Name        201
    name             ${EMPTY}          400
    name             ${NONE}           400


*** Keywords ***
Create API Session
    [Documentation]    Create a reusable HTTP session with auth headers
    ${headers}=    Create Dictionary
    ...    Authorization=Bearer ${AUTH_TOKEN}
    ...    Content-Type=application/json
    Create Session    api    ${API_BASE_URL}    headers=${headers}    verify=${True}

POST And Verify Status
    [Arguments]    ${key}    ${value}    ${expected_status}
    [Documentation]    Template keyword for data-driven API tests
    ${payload}=    Create Dictionary    ${key}=${value}
    ${response}=    POST On Session    api    ${ENDPOINT}
    ...    json=${payload}    expected_status=${expected_status}
    Status Should Be    ${expected_status}    ${response}
