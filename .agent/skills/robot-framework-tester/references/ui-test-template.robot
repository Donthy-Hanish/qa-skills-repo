*** Settings ***
Documentation     Template for UI test suite files using SeleniumLibrary.
...               Copy and customize for each feature/page under test.
Library           SeleniumLibrary
Library           Collections
Resource          resources/<page_name>_page.resource
Resource          resources/common.resource
Variables         variables/variables.robot

Suite Setup       Open Browser And Login
Suite Teardown    Close All Browsers
Test Setup        Go To    ${BASE_URL}/<page_path>
Test Teardown     Run Keyword If Test Failed    Capture Page Screenshot

Force Tags        <feature-tag>


*** Variables ***
# Test-specific variables that don't belong in the shared variables file
${VALID_INPUT}        example_value
${INVALID_INPUT}      !@#$%^


*** Test Cases ***
# --- SMOKE TESTS ---

Verify <Page/Feature> Loads Successfully
    [Documentation]    Confirm the page renders without errors
    [Tags]    smoke    critical
    Wait Until Element Is Visible    ${PAGE_HEADER}
    Element Text Should Be    ${PAGE_HEADER}    Expected Header Text

# --- POSITIVE TESTS ---

<Descriptive Test Name>
    [Documentation]    <What this test validates and why it matters>
    [Tags]    regression    high    <feature-tag>
    <Step using Page Object keyword>
    <Verification step>

# --- NEGATIVE TESTS ---

<Descriptive Negative Test Name>
    [Documentation]    <What invalid scenario this covers>
    [Tags]    regression    medium    <feature-tag>
    <Step that triggers the error>
    <Verification of error handling>

# --- DATA-DRIVEN TESTS ---

<Template Test Name>
    [Documentation]    Data-driven test covering multiple input combinations
    [Tags]    regression    high    <feature-tag>    data-driven
    [Template]    <Template Keyword Name>
    # input_1    input_2    expected_result
    valid_a      valid_b    Success
    empty        valid_b    Field required
    valid_a      invalid    Invalid format


*** Keywords ***
Open Browser And Login
    [Documentation]    Suite-level setup: launch browser and authenticate
    Open Browser    ${BASE_URL}    ${BROWSER}
    ...    options=add_argument("--headless");add_argument("--no-sandbox")
    Maximize Browser Window
    Login As    ${DEFAULT_USER}    ${DEFAULT_PASSWORD}

<Template Keyword Name>
    [Arguments]    ${input_1}    ${input_2}    ${expected}
    [Documentation]    Template keyword for data-driven tests
    Fill Field    ${INPUT_1_LOCATOR}    ${input_1}
    Fill Field    ${INPUT_2_LOCATOR}    ${input_2}
    Click Submit
    Verify Result    ${expected}
