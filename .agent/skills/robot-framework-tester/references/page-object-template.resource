*** Settings ***
Documentation     Page Object template for <Page Name>.
...               Contains locators and keywords for interacting with the <page>.
Library           SeleniumLibrary


*** Variables ***
# --- Locators ---
${PAGE_HEADER}            css:h1.page-title
${INPUT_USERNAME}         id:username
${INPUT_PASSWORD}         id:password
${BTN_SUBMIT}             css:button[type="submit"]
${MSG_ERROR}              css:.error-message
${MSG_SUCCESS}            css:.success-banner
${LOADING_SPINNER}        css:.spinner


*** Keywords ***
Fill Login Form
    [Documentation]    Enter username and password into the login form.
    [Arguments]    ${username}    ${password}
    Wait Until Element Is Visible    ${INPUT_USERNAME}    timeout=10s
    Input Text    ${INPUT_USERNAME}    ${username}
    Input Text    ${INPUT_PASSWORD}    ${password}

Click Submit Button
    [Documentation]    Click the submit button and wait for navigation or response.
    Wait Until Element Is Enabled    ${BTN_SUBMIT}    timeout=5s
    Click Element    ${BTN_SUBMIT}
    Wait Until Element Is Not Visible    ${LOADING_SPINNER}    timeout=15s

Verify Error Message Is Displayed
    [Documentation]    Assert that the error message element is visible with expected text.
    [Arguments]    ${expected_message}
    Wait Until Element Is Visible    ${MSG_ERROR}    timeout=5s
    Element Text Should Be    ${MSG_ERROR}    ${expected_message}

Verify Success Message Is Displayed
    [Documentation]    Assert that the success banner appears with expected text.
    [Arguments]    ${expected_message}
    Wait Until Element Is Visible    ${MSG_SUCCESS}    timeout=10s
    Element Text Should Be    ${MSG_SUCCESS}    ${expected_message}
