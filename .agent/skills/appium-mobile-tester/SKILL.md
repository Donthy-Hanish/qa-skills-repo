---
name: appium-mobile-tester
description: "Generate Python + pytest + Appium test suites for mobile apps - native Android, iOS, React Native, Flutter, or hybrid. Covers POM, locator chains, gestures, and cross-platform configs."
version: "1.0.2"
---

# Appium Mobile Tester

You are helping the user generate production-quality mobile test automation using Python + pytest + Appium. The user has strong QA Automation and Python background but is new to mobile testing. Explain mobile-specific concepts clearly when they first appear.

## When to Use

Use this skill when:

- The user wants to write automated tests for a mobile app (any framework: React Native, native Android/iOS, Flutter, hybrid)
- The user asks about Appium setup, capabilities, drivers, or mobile element locators
- The user provides a screen description, user story, or feature spec and wants mobile E2E tests
- The user wants to set up cross-platform test execution (same tests running on Android and iOS)
- The user asks about mobile gestures (swipe, scroll, tap, long press, pinch)
- The user wants to integrate mobile tests into CI/CD
- The user asks about device cloud integration (BrowserStack, Sauce Labs, AWS Device Farm)
- The user mentions myProlink or any other mobile app by name in a testing context

Do NOT use this skill when:

- The user wants Maestro YAML flows (use maestro-flow-tester)
- The user wants XCUITest with Swift or Espresso with Kotlin as the primary framework
- The user wants web browser testing only (use standard Playwright/Selenium skills)
- The user wants mobile performance/load testing (use ui-load-test)

## Prerequisites

Before generating tests, verify the environment. Run `scripts/verify-setup.sh` or check manually:

```bash
python3 --version          # 3.9+
appium --version           # Appium 2.x
adb devices                # Android SDK installed, devices/emulators visible
# For iOS: xcrun simctl list  # Xcode + simulators available
```

Required Python packages (install via `pip install`):

```
Appium-Python-Client>=4.0.0
pytest>=7.0
pytest-html>=4.0
```

Full dependency declaration is in `requirements.json` at skill root.

## Core Concepts for the Beginner

Mobile testing differs from web testing in several important ways. Read `references/mobile-testing-basics.md` the first time the user encounters any of these concepts:

- **Desired Capabilities** - a JSON config that tells Appium which device, OS, and app to automate
- **Appium Drivers** - UiAutomator2 for Android, XCUITest for iOS (yes, Appium uses XCUITest under the hood)
- **Element Locators on Mobile** - accessibility ID, resource-id, XPath, class chain, predicate string
- **Emulator vs Real Device** - trade-offs in speed, accuracy, and cost
- **App Installation** - Appium installs the .apk (Android) or .ipa/.app (iOS) automatically via capabilities
- **Context Switching** - moving between NATIVE_APP and WEBVIEW contexts in hybrid/React Native apps

## Routing - Determine What the User Needs

Before generating code, classify the request:

- IF the user provides a screen/feature description and wants test cases --> Generate Test Suite Flow
- IF the user wants to set up Appium from scratch --> Setup Flow
- IF the user has failing tests and wants to debug --> Debug Flow
- IF the user wants to add gesture testing (swipe, scroll, drag) --> Gesture Flow
- IF the user wants to run tests on a device cloud --> Cloud Integration Flow
- IF the user wants to run existing tests cross-platform --> Cross-Platform Config Flow

## Generate Test Suite Flow

This is the primary workflow. Given a screen or feature, generate a complete test suite.

### Step 1 - Gather Context

Ask or infer:

1. **App type**: React Native, native Android, native iOS, Flutter, hybrid?
2. **Platform target**: Android only, iOS only, or both?
3. **Screen/feature**: What is being tested? (login, dashboard, search, checkout, etc.)
4. **Test data**: Any required users, accounts, or preconditions?
5. **Known element IDs**: Does the dev team use testID/accessibilityLabel? If unknown, assume they need guidance on adding them.

IF the user does not specify the app type, default to React Native (the most common case in this user's projects). State the assumption.

### Step 2 - Generate the Page Object

Every screen gets a Page Object. This is non-negotiable - never put locators directly in test methods.

**Page Object pattern with multi-strategy locators:**

```python
"""
Page Object for [ScreenName]
App: [AppName]
Platform: Cross-platform (Android + iOS)
"""
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    """Page Object for the Login screen."""

    # --- Locator strategies (ordered by resilience) ---
    # Strategy 1: accessibility_id (cross-platform, most stable)
    # Strategy 2: resource-id / name (platform-specific, stable if devs maintain)
    # Strategy 3: xpath (fragile, last resort)

    LOCATORS = {
        "username_field": [
            (AppiumBy.ACCESSIBILITY_ID, "username-input"),
            (AppiumBy.ID, "com.app.package:id/username_field"),
            (AppiumBy.XPATH, "//android.widget.EditText[@text='Username']"),
        ],
        "password_field": [
            (AppiumBy.ACCESSIBILITY_ID, "password-input"),
            (AppiumBy.ID, "com.app.package:id/password_field"),
            (AppiumBy.XPATH, "//android.widget.EditText[@text='Password']"),
        ],
        "login_button": [
            (AppiumBy.ACCESSIBILITY_ID, "login-button"),
            (AppiumBy.ID, "com.app.package:id/btn_login"),
            (AppiumBy.XPATH, "//android.widget.Button[@text='Login']"),
        ],
    }

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def find_element(self, element_name):
        """Try each locator strategy in order until one works."""
        strategies = self.LOCATORS.get(element_name, [])
        last_exception = None
        for by, value in strategies:
            try:
                element = self.wait.until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except Exception as e:
                last_exception = e
                continue
        raise last_exception or Exception(
            f"Element '{element_name}' not found with any strategy"
        )

    def enter_username(self, username):
        """Clear and type username."""
        field = self.find_element("username_field")
        field.clear()
        field.send_keys(username)

    def enter_password(self, password):
        """Clear and type password."""
        field = self.find_element("password_field")
        field.clear()
        field.send_keys(password)

    def tap_login(self):
        """Tap the login button."""
        self.find_element("login_button").click()

    def login(self, username, password):
        """Convenience method: full login flow."""
        self.enter_username(username)
        self.enter_password(password)
        self.tap_login()
```

**Key rules for Page Objects:**

- One class per screen, one file per class
- Multi-strategy locators in a LOCATORS dict, ordered by resilience
- The `find_element` fallback method is mandatory - this is the practical self-healing layer
- Action methods (enter_username, tap_login) call find_element, never use raw locators
- Add docstrings explaining what each action does
- Name files as `page_<screen_name>.py` (e.g., `page_login.py`, `page_dashboard.py`)

### Step 3 - Generate the Test Module

Tests use pytest and follow this structure:

```python
"""
Test suite for [FeatureName]
App: [AppName]
Platform: [Android/iOS/Both]
"""
import pytest
from pages.page_login import LoginPage

class TestLogin:
    """Tests for the Login screen."""

    def test_successful_login(self, driver):
        """Verify user can log in with valid credentials."""
        login_page = LoginPage(driver)
        login_page.login("test_user_01", "SecurePass123!")
        # Assert navigation to dashboard
        assert driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "dashboard-header"
        ).is_displayed()

    def test_login_empty_username(self, driver):
        """Verify error when username is empty."""
        login_page = LoginPage(driver)
        login_page.enter_password("SecurePass123!")
        login_page.tap_login()
        error = login_page.find_element("error_message")
        assert "username" in error.text.lower()

    def test_login_invalid_password(self, driver):
        """Verify error when password is wrong."""
        login_page = LoginPage(driver)
        login_page.login("test_user_01", "WrongPassword!")
        error = login_page.find_element("error_message")
        assert "invalid" in error.text.lower() or "incorrect" in error.text.lower()

    def test_password_field_masks_input(self, driver):
        """Verify password field obscures characters."""
        login_page = LoginPage(driver)
        field = login_page.find_element("password_field")
        field.send_keys("TestPass")
        # On Android, check the 'password' attribute
        # On iOS, check 'secureTextEntry'
        is_secure = (
            field.get_attribute("password") == "true"
            or field.get_attribute("secureTextEntry") == "true"
        )
        assert is_secure
```

**Key rules for test modules:**

- One test class per feature/screen
- Test method names follow `test_<action>_<expected_outcome>` pattern
- Each test is independent - no test depends on another test's state
- Use meaningful domain-appropriate test data names (never "test123" or "foo")
- Assertions are explicit with descriptive failure messages
- Platform-specific assertions are clearly commented

### Step 4 - Generate the conftest.py (Fixtures)

The conftest.py manages driver setup/teardown and is the single place where capabilities are configured:

```python
"""
Appium driver fixtures for pytest.
Reads platform config from environment or defaults to Android.
"""
import os
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

def get_android_options():
    """Build Android UiAutomator2 capabilities."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = os.getenv("ANDROID_DEVICE", "emulator-5554")
    options.app = os.getenv("ANDROID_APP_PATH", "./apps/app-debug.apk")
    options.automation_name = "UiAutomator2"
    options.no_reset = False
    options.full_reset = False
    # React Native: enable accessibility hierarchy
    options.set_capability("appium:ensureWebviewsHavePages", True)
    return options

def get_ios_options():
    """Build iOS XCUITest capabilities."""
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.device_name = os.getenv("IOS_DEVICE", "iPhone 15")
    options.platform_version = os.getenv("IOS_VERSION", "17.0")
    options.app = os.getenv("IOS_APP_PATH", "./apps/MyApp.app")
    options.automation_name = "XCUITest"
    options.no_reset = False
    options.full_reset = False
    return options

@pytest.fixture(scope="function")
def driver(request):
    """Create and yield an Appium driver, then quit after test."""
    platform = os.getenv("TEST_PLATFORM", "android").lower()

    if platform == "android":
        options = get_android_options()
    elif platform == "ios":
        options = get_ios_options()
    else:
        raise ValueError(f"Unknown platform: {platform}")

    appium_server = os.getenv("APPIUM_SERVER", "http://localhost:4723")

    driver = webdriver.Remote(
        command_executor=appium_server,
        options=options,
    )
    driver.implicitly_wait(10)

    yield driver

    driver.quit()
```

**Key rules for conftest.py:**

- Capabilities come from environment variables with sensible defaults
- One fixture, two platforms - switch via `TEST_PLATFORM` env var
- Scope is `function` (each test gets a fresh driver) unless the user explicitly requests session-level
- Always `driver.quit()` in teardown - leaked sessions break Appium server
- Use Appium 2.x Options classes, not the deprecated `desired_capabilities` dict

### Step 5 - Generate the Project Structure

Every generated suite follows this layout:

```
mobile-tests/
  conftest.py              # Driver fixtures + capabilities
  pytest.ini               # Pytest config (markers, reporting)
  requirements.txt         # Python dependencies
  apps/                    # .apk and .app/.ipa files (gitignored)
  pages/                   # Page Objects
    __init__.py
    page_login.py
    page_dashboard.py
  tests/                   # Test modules
    __init__.py
    test_login.py
    test_dashboard.py
  configs/                 # Per-device capability overrides (optional)
    android_pixel7.json
    ios_iphone15.json
  reports/                 # pytest-html output (gitignored)
```

Generate a `pytest.ini`:

```ini
[pytest]
markers =
    smoke: Quick validation tests
    regression: Full regression suite
    android: Android-specific tests
    ios: iOS-specific tests
    cross_platform: Tests that run on both platforms
testpaths = tests
addopts = --html=reports/report.html --self-contained-html -v
```

## Gesture Flow

When the user needs gesture testing (swipe, scroll, long press, pinch), generate a `utils/gestures.py` helper module.

**Key rules for gestures:**
- Always use W3C Actions API (`ActionBuilder` + `PointerInput`), never the deprecated `TouchAction`
- Calculate coordinates from `driver.get_window_size()`, never hardcode pixel values
- Provide `swipe(driver, direction)`, `scroll_to_element(driver, locator, max_scrolls)`, and `long_press(driver, element, duration_ms)` as the core helpers
- Swipe offset should be roughly one-third of screen dimension to avoid over/under-scrolling

See `references/mobile-testing-basics.md` Section 9 for gesture types. Generate the full gesture utility code following the W3C Actions pattern when this flow triggers.

## Cloud Integration Flow

When the user wants BrowserStack, Sauce Labs, or AWS Device Farm integration, update conftest.py to support remote execution:

- Add a cloud capability builder function that reads credentials from environment variables (never hardcode)
- Switch the Appium server URL to the cloud provider endpoint
- Add device config JSON files under `configs/` for each target device
- Include instructions for uploading the app binary to the cloud provider before running

See `references/capability-reference.md` Section 5 for complete BrowserStack, Sauce Labs, and AWS Device Farm capability examples.

## Cross-Platform Config Flow

When the same test needs to run on both Android and iOS, use pytest parametrize at the fixture level in conftest.py:

```python
@pytest.fixture(params=["android", "ios"])
def cross_platform_driver(request):
    """Parametrized fixture that runs each test on both platforms."""
    platform = request.param
    options = get_android_options() if platform == "android" else get_ios_options()
    appium_server = os.getenv("APPIUM_SERVER", "http://localhost:4723")
    driver = webdriver.Remote(command_executor=appium_server, options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()
```

Tests using `cross_platform_driver` instead of `driver` will automatically run twice - once per platform.

## Anti-Patterns - Things That Will Break Your Tests

| Anti-pattern | Why it breaks | Do this instead |
|---|---|---|
| Hardcoding locators in test methods | One UI change breaks every test that uses that locator | Use Page Objects with LOCATORS dict |
| Using only XPath | Slow on mobile, fragile to hierarchy changes, different between Android and iOS | Prefer accessibility_id, fall back through the strategy chain |
| Using `time.sleep()` for waits | Flaky - too short and tests fail, too long and suite is slow | Use WebDriverWait with expected_conditions |
| Sharing state between tests | Test A passes, test B depends on A's result, test A fails and B fails for the wrong reason | Each test starts from a known state via fixture setup |
| Using `desired_capabilities` dict | Deprecated in Appium 2.x, will break with future Appium updates | Use Options classes (UiAutomator2Options, XCUITestOptions) |
| Not quitting the driver | Orphaned sessions pile up and crash the Appium server | Always quit in fixture teardown |
| Ignoring implicit vs explicit wait conflicts | Implicit wait + explicit wait compound into unpredictable timeouts | Use explicit waits only, set implicit to 0 if using explicit extensively |
| Testing on emulator only | Emulators miss real device issues: touch accuracy, performance, camera, biometrics | Test on at least one real device or device cloud before release |
| Assuming same locators work on both platforms | Android resource-id and iOS accessibility identifier are different attributes | Use accessibility_id for cross-platform, or maintain per-platform locator maps |
| Not setting `noReset`/`fullReset` deliberately | App state leaks between tests, or app reinstalls every test making suite painfully slow | Set noReset=False, fullReset=False as default, use fullReset only for setup-sensitive tests |
| Generating test data like "test123", "user1", "abc" | Meaningless data hides bugs and makes failures unreadable | Use domain-appropriate data: "priya.sharma@company.com", "Warehouse-Mumbai-03" |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| "Could not start a new session" | Appium server not running, or wrong capabilities | Run `scripts/verify-setup.sh`, check server URL and port |
| "An element could not be located" | Locator is wrong, or element not yet rendered | Check with Appium Inspector, add explicit wait, verify locator strategy |
| Tests pass on Android, fail on iOS | Different element tree structure | Add iOS-specific locators to LOCATORS dict |
| "Original error: Could not proxy" | UiAutomator2/XCUITest driver not installed | Run `appium driver install uiautomator2` or `appium driver install xcuitest` |
| Gestures do nothing | Coordinates out of bounds, or wrong touch action API | Use W3C Actions API (not deprecated TouchAction), verify coordinates with window_size |
| Tests are extremely slow | Implicit wait too high, or fullReset=True on every test | Set implicit wait to 5-10s max, use noReset unless state isolation is critical |
| React Native elements not found | Need to switch to correct context (NATIVE vs WEBVIEW) | Check `driver.contexts`, switch with `driver.switch_to.context()` |

## Reference Files

| File | What it is | When to load |
|---|---|---|
| `references/mobile-testing-basics.md` | Beginner-friendly guide to mobile testing concepts | First time user encounters mobile-specific concepts, or on any Setup Flow request |
| `references/locator-strategy-guide.md` | Deep dive on locator strategies per platform with Appium Inspector walkthrough | When user asks about finding elements, building locators, or debugging "element not found" |
| `references/capability-reference.md` | Common capabilities for Android, iOS, React Native, Flutter, with explanations | When generating conftest.py or when user asks about capabilities |

## Scripts

| Script | Purpose | When to run |
|---|---|---|
| `scripts/verify-setup.sh` | Check Appium, ADB, Node.js, Python, and connected devices | Before first test run, or when "Could not start session" errors appear |
| `scripts/list-devices.sh` | List all connected Android devices/emulators and iOS simulators | When user needs to pick a device_name for capabilities |
| `scripts/inspect-app-elements.py` | Dump the current screen's element tree to help find locators | When building Page Objects for a new screen |

## Examples

### Example 1 - User provides a screen description

**User says:** "Write Appium tests for the myProlink login screen. It has email and password fields, a login button, and a forgot password link. React Native, both platforms."

**Expected output:**
1. conftest.py with Android + iOS capabilities
2. pages/page_login.py with multi-strategy locators for all four elements
3. tests/test_login.py with tests for: successful login, empty email, empty password, invalid credentials, forgot password navigation, password masking
4. pytest.ini with markers
5. requirements.txt

### Example 2 - User wants gesture tests

**User says:** "Add swipe tests for the onboarding carousel. Three slides, swipe left to advance."

**Expected output:**
1. pages/page_onboarding.py with locators for slide indicators and content
2. utils/gestures.py with swipe helper
3. tests/test_onboarding.py with tests for: swipe through all slides, swipe back, skip button, final slide CTA

### Example 3 - User wants cloud integration

**User says:** "Run my existing tests on BrowserStack across 3 Android devices."

**Expected output:**
1. Updated conftest.py with BrowserStack capability builder
2. configs/browserstack_devices.json with 3 device configs
3. Instructions for uploading the APK and setting environment variables

## Changelog

- **1.0.0** - Initial release. Python + pytest + Appium 2.x with Page Object Model, multi-strategy locator chains, cross-platform capability configs, gesture utilities, cloud integration, anti-patterns table, troubleshooting guide, and beginner-friendly reference docs.
