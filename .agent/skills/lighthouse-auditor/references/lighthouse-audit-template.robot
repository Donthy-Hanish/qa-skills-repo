*** Settings ***
Documentation     Lighthouse Performance and Quality Audit Test Suite Template
Library           lighthouse-keywords.py
Suite Setup       Suite Setup Actions
Suite Teardown    Suite Teardown Actions
Force Tags        performance    lighthouse

*** Variables ***
${BASE_URL}             https://example.com
${LOGIN_URL}            https://example.com/login
${USERNAME}             testuser
${PASSWORD}             password123
${MIN_PERF_SCORE}       80
${MIN_A11Y_SCORE}       90
${PRESET}               desktop
${USER_FLOW_SCRIPT}     ${CURDIR}/user-flow-example.js

*** Test Cases ***
Smoke Test: Single Page Performance Check
    [Documentation]    Runs a quick Lighthouse audit on the homepage and asserts basic scores.
    [Tags]             smoke
    ${result}=         Run Lighthouse Audit    ${BASE_URL}    preset=${PRESET}
    Assert Performance Score     ${result}    ${MIN_PERF_SCORE}
    Assert Accessibility Score   ${result}    ${MIN_A11Y_SCORE}
    Assert SEO Score             ${result}    90

Core Web Vitals Assertion Test
    [Documentation]    Verifies that the Core Web Vitals meet Google's recommended thresholds.
    [Tags]             smoke
    ${result}=         Run Lighthouse Audit    ${BASE_URL}    preset=${PRESET}
    Assert LCP Under Threshold    ${result}    max_ms=2500
    Assert CLS Under Threshold    ${result}    max_value=0.1
    ${vitals}=         Extract Core Web Vitals    ${result}
    Log Many           LCP: ${vitals}[LCP] ms    FID: ${vitals}[FID] ms    CLS: ${vitals}[CLS]    TBT: ${vitals}[TBT] ms    SI: ${vitals}[SI] ms

Regression Test: Audit Multiple Pages From List
    [Documentation]    Runs a batch audit on a list of site sections.
    [Tags]             regression
    @{urls}=           Create List    ${BASE_URL}    ${BASE_URL}/about    ${BASE_URL}/contact
    ${results}=        Run Batch Audit    ${urls}    preset=${PRESET}
    FOR    ${res}    IN    @{results}
        Log    Audited URL: ${res}[url]
        Assert Performance Score    ${res}    70
    END

Data-Driven Audit Check
    [Documentation]    Data-driven test using template to check different pages with individual thresholds.
    [Tags]             regression
    [Template]         Audit URL and Assert Custom Thresholds
    # URL                           # Min Perf   # Min A11y
    ${BASE_URL}                     80           90
    ${BASE_URL}/about               75           85
    ${BASE_URL}/contact             70           80

Audit Authenticated Dashboard Page
    [Documentation]    Logs into the site first, grabs the session cookies, and runs a Lighthouse audit behind the login gate.
    [Tags]             authenticated
    ${result}=         Run Authenticated Lighthouse Audit    ${BASE_URL}/dashboard    ${LOGIN_URL}    ${USERNAME}    ${PASSWORD}    \#username    \#password    \#submit-btn    preset=${PRESET}
    Assert Performance Score     ${result}    ${MIN_PERF_SCORE}
    Assert Accessibility Score   ${result}    ${MIN_A11Y_SCORE}

Audit Checkout Flow As A User Flow
    [Documentation]    Runs a multi-step user flow (navigation, timespan, snapshot) using Puppeteer and Lighthouse.
    [Tags]             user-flow
    ${result}=         Run Lighthouse User Flow    ${USER_FLOW_SCRIPT}
    Assert Performance Score     ${result}    75
    Assert Accessibility Score   ${result}    80

Compare Cold Vs Warm Page Load Scores
    [Documentation]    Runs two navigations to the same URL — first a cold load (cache cleared),
    ...                then a warm load (disableStorageReset: true) — and logs both performance
    ...                scores so you can see the caching improvement.
    [Tags]             performance    regression
    ${flow_result}=    Run Warm Navigation Audit    ${BASE_URL}    preset=${PRESET}
    Log    Cold vs Warm flow completed — check reports/warm_nav_flow.json for per-step scores.

Audit Checkout Form Accessibility Mid-Completion
    [Documentation]    Navigates to the checkout page, fills in form fields to reach a
    ...                mid-completion state, then takes a Lighthouse snapshot. Snapshot mode
    ...                tests accessibility and best practices on the current DOM — it does
    ...                NOT reload the page, so it captures the exact state of the form.
    [Tags]             accessibility    snapshot
    ${interaction}=    Set Variable    await page.type('#first-name', 'Jane'); await page.type('#last-name', 'Doe'); await page.type('#email', 'jane@example.com');
    ${result}=         Run Snapshot Audit    ${BASE_URL}/checkout    interaction_js=${interaction}    preset=${PRESET}
    Assert Accessibility Score    ${result}    ${MIN_A11Y_SCORE}

Measure Layout Shift During Product Scroll
    [Documentation]    Opens the products page, starts a Lighthouse timespan, scrolls through
    ...                the product grid (triggering lazy-load images and layout shifts), then
    ...                ends the timespan. The resulting CLS and TBT values reflect what real
    ...                users experience during scrolling.
    [Tags]             performance    timespan
    ${scroll_js}=      Set Variable    for (let i = 0; i < 5; i++) { await page.evaluate(() => window.scrollBy(0, 800)); await new Promise(r => setTimeout(r, 500)); }
    ${result}=         Run Timespan Audit    ${BASE_URL}/products    interaction_js=${scroll_js}    preset=${PRESET}
    ${vitals}=         Extract Core Web Vitals    ${result}
    Log    CLS during scroll: ${vitals}[CLS]
    Log    TBT during scroll: ${vitals}[TBT]

*** Keywords ***
Suite Setup Actions
    Log    Initializing Lighthouse Audit Test Suite...
    Log    Targeting Base URL: ${BASE_URL} with Preset: ${PRESET}

Suite Teardown Actions
    Log    Lighthouse Performance and Quality Audit Suite Execution Completed.

Audit URL and Assert Custom Thresholds
    [Arguments]    ${url}    ${min_perf}    ${min_a11y}
    Log    Auditing: ${url}
    ${result}=     Run Lighthouse Audit    ${url}    preset=${PRESET}
    Assert Performance Score     ${result}    ${min_perf}
    Assert Accessibility Score   ${result}    ${min_a11y}

