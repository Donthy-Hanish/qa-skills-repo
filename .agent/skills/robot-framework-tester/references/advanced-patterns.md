# Robot Framework Advanced Patterns

This reference guide details advanced engineering patterns for Robot Framework, including data-driven testing, parallel execution matrices, database verification, custom listeners, and environment configurations.

---

## 1. Data-Driven Testing (CSV)

The `robotframework-datadriver` library allows you to run a single test template multiple times using data loaded from an external CSV file.

### Installation
```bash
pip install robotframework-datadriver
```

### CSV File (`test_data.csv`)
# Note: DataDriver automatically maps plain column names to Robot variables.
username,password,expected_error
invalid_user,wrong_pass,Invalid username or password
empty_user,,Username cannot be empty
good_user,wrong_pass,Invalid username or password
```

### Robot Code (`login_data_driven.robot`)
```robot
*** Settings ***
Documentation     Data-driven UI login tests using DataDriver and CSV.
Library           SeleniumLibrary
Library           DataDriver    file=test_data.csv
Suite Setup       Open Browser To Login Page
Suite Teardown    Close Browser
Test Setup        Go To Login Page
Test Template     Verify Login Failures

*** Test Cases ***
Login With Invalid Credentials    ${username}    ${password}    ${expected_error}

*** Keywords ***
Open Browser To Login Page
    Open Browser    https://example.com/login    chrome

Go To Login Page
    Go To    https://example.com/login

Verify Login Failures
    [Arguments]    ${username}    ${password}    ${expected_error}
    Input Text      id=username    ${username}
    Input Text      id=password    ${password}
    Click Button    id=login-btn
    Wait Until Element Is Visible    id=error-msg
    Element Text Should Be           id=error-msg    ${expected_error}
```

---

## 2. Data-Driven Testing (YAML)

To drive tests using nested or structured data, load variables directly from YAML files.

### YAML File (`test_data.yaml`)
```yaml
user_credentials:
  admin:
    username: "admin_user"
    password: "secure_admin_pass"
  guest:
    username: "guest_user"
    password: "guest_password"
```

### Robot Code (`yaml_driven.robot`)

> [!NOTE]
> Dot-notation access (`${user_credentials.admin.username}`) works with Python variable files. If using Robot's standard YAML `Variables` import, use bracket notation instead: `${user_credentials}[admin][username]`.

```robot
*** Settings ***
Documentation     Suite leveraging external YAML variables.
Variables         test_data.yaml
Library           SeleniumLibrary

*** Test Cases ***
Verify Admin Login
    [Setup]    Open Login Page
    Login As User    ${user_credentials}[admin][username]    ${user_credentials}[admin][password]
    Verify Welcome Message for Admin
    [Teardown]    Close Browser

*** Keywords ***
Open Login Page
    Open Browser    https://example.com/login    chrome

Login As User
    [Arguments]    ${username}    ${password}
    Input Text      id=username    ${username}
    Input Text      id=password    ${password}
    Click Button    id=login-btn
```

---

## 3. Parallel Execution Browser Matrix (Pabot)

Run a test suite across a matrix of multiple browsers concurrently using `pabot`.

### Argument files setup
Create argument files specifying the configurations:

**`chrome.args`**
```txt
--variable BROWSER:chrome
--outputdir results/chrome
```

**`firefox.args`**
```txt
--variable BROWSER:firefox
--outputdir results/firefox
```

### Execution Command
Run pabot using the `--argumentfile` options to execute your tests in parallel against the matrix:
```bash
pabot --argumentfile1 chrome.args --argumentfile2 firefox.args tests/
```

---

## 4. Database Verification (DatabaseLibrary)

Validate data state in relational databases to confirm that backend actions match the front-end or API results.

### Installation
```bash
pip install robotframework-databaselibrary psycopg2-binary
```

### Database Verification Example
```robot
*** Settings ***
Library           DatabaseLibrary
Suite Setup       Connect To Customer DB
Suite Teardown    Disconnect From Database

*** Variables ***
${DB_NAME}        postgres
${DB_USER}        db_user
${DB_PASS}        secret_db_pass
${DB_HOST}        localhost
${DB_PORT}        5432

*** Test Cases ***
Verify Customer Record Insertion
    [Documentation]    Creates a user, queries DB to verify, and deletes record.
    ...                NOTE: 'Generate Random User ID' and 'Create User Via API' are placeholder keywords.
    ...                You must implement these in your project's .resource file or Python library before running this example.
    ${user_id}=        Generate Random User ID
    Create User Via API    ${user_id}    John Doe
    
    # Database Verification
    Check If Exists In Database    SELECT id FROM users WHERE id = '${user_id}' AND name = 'John Doe'
    @{query_results}=  Query       SELECT email FROM users WHERE id = '${user_id}'
    Should Be Equal As Strings    ${query_results[0][0]}    john.doe@example.com
    
    [Teardown]         Run Keyword And Ignore Error    Delete Customer Record    ${user_id}

*** Keywords ***
Connect To Customer DB
    Connect To Database    psycopg2    ${DB_NAME}    ${DB_USER}    ${DB_PASS}    ${DB_HOST}    ${DB_PORT}

Delete Customer Record
    [Arguments]    ${user_id}
    Execute Sql String    DELETE FROM users WHERE id = '${user_id}'
```

---

## 5. Complex Keyword Composition

Combine low-level keywords into high-level business flows and use native control flow.

### Keyword Chains and Native IF/ELSE
Robot Framework 5.0+ introduces native `IF`, `ELSE IF`, `ELSE`, and `FOR` blocks which should be preferred over `Run Keyword If`.

```robot
*** Keywords ***
Complete Checkout Process
    [Documentation]    High-level composite keyword (Keyword Chain)
    Navigate To Shopping Cart
    Proceed To Checkout
    Fill Shipping Information
    Select Payment Method
    Submit Order

Process Dynamic Payment
    [Arguments]    ${payment_type}    ${amount}
    IF  '${payment_type}' == 'CreditCard'
        Process Credit Card Payment    ${amount}
    ELSE IF  '${payment_type}' == 'PayPal'
        Process PayPal Payment    ${amount}
    ELSE
        Fail    Unsupported payment type: ${payment_type}
    END
```

---

## 6. Custom Listeners for Real-Time Reporting

Listeners allow you to execute custom Python code during various phases of test execution (e.g., when a test starts, ends, or fails).

### Python Listener (`ConsoleProgressReport.py`)
```python
import sys

class ConsoleProgressReport:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, environment="staging"):
        self.environment = environment

    def start_test(self, name, attributes):
        sys.stdout.write(f"\n🚀 Starting: {name} [Tags: {', '.join(attributes['tags'])}]\n")
        sys.stdout.flush()

    def end_test(self, name, attributes):
        status = attributes['status']
        symbol = "✅" if status == "PASS" else "❌"
        sys.stdout.write(f"{symbol} Finished: {name} | Status: {status} | Elapsed: {attributes['elapsedtime']}ms\n")
        if status == "FAIL":
            sys.stdout.write(f"   Reason: {attributes['message']}\n")
        sys.stdout.flush()
```

### Execution
Run tests with the listener registered:
```bash
robot --listener ConsoleProgressReport.py:production tests/
```

---

## 7. Environment-Specific Variable Files

Manage variables per environment (Dev, Staging, Prod) by using YAML variables files and loading the correct file at runtime.

### Variable Files

**`dev.yaml`**
```yaml
BASE_URL: "https://dev.app.internal"
API_URL: "https://dev-api.app.internal"
DB_HOST: "dev-db.internal"
```

**`staging.yaml`**
```yaml
BASE_URL: "https://staging.app.internal"
API_URL: "https://staging-api.app.internal"
DB_HOST: "staging-db.internal"
```

### Execution Command
Execute tests against staging:
```bash
robot --variablefile staging.yaml tests/
```
