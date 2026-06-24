# Capability Reference

Common Appium capabilities for Android, iOS, React Native, and Flutter apps with explanations.

## Table of Contents

1. Android UiAutomator2 Capabilities
2. iOS XCUITest Capabilities
3. React Native-Specific Capabilities
4. Flutter-Specific Capabilities
5. Device Cloud Capabilities (BrowserStack, Sauce Labs)
6. Environment Variable Pattern

---

## 1. Android UiAutomator2 Capabilities

```python
from appium.options.android import UiAutomator2Options

options = UiAutomator2Options()

# --- Required ---
options.platform_name = "Android"
options.automation_name = "UiAutomator2"
options.device_name = "emulator-5554"       # From 'adb devices'
options.app = "./apps/myapp-debug.apk"      # Path to APK

# --- App state ---
options.no_reset = False                    # Clear app data before session
options.full_reset = False                  # Do not uninstall/reinstall

# --- Timeouts ---
options.new_command_timeout = 300           # Seconds before idle session dies
options.set_capability("appium:uiautomator2ServerLaunchTimeout", 60000)

# --- Permissions ---
options.auto_grant_permissions = True       # Auto-accept permission dialogs

# --- Performance ---
options.set_capability("appium:skipDeviceInitialization", True)   # Faster start
options.set_capability("appium:skipServerInstallation", True)     # Skip if already installed

# --- Useful for debugging ---
options.set_capability("appium:printPageSourceOnFindFailure", True)
```

**Capability explanations:**

| Capability | Type | Default | What it does |
|---|---|---|---|
| `platformName` | Required | - | Must be "Android" |
| `automationName` | Required | - | Must be "UiAutomator2" for Appium 2.x |
| `deviceName` | Required | - | Device serial from `adb devices` |
| `app` | Required* | - | Path to .apk. Not needed if `appPackage` + `appActivity` are set |
| `appPackage` | Optional | - | Java package name (e.g., `com.myapp.prolink`). Use instead of `app` if already installed |
| `appActivity` | Optional | - | Activity to launch (e.g., `.MainActivity`) |
| `noReset` | Optional | false | Keep app data between sessions |
| `fullReset` | Optional | false | Uninstall and reinstall the app |
| `autoGrantPermissions` | Optional | false | Auto-grant runtime permissions |
| `newCommandTimeout` | Optional | 60 | Seconds before idle timeout |
| `chromedriverExecutable` | Optional | - | Path to specific ChromeDriver for WebView testing |

---

## 2. iOS XCUITest Capabilities

```python
from appium.options.ios import XCUITestOptions

options = XCUITestOptions()

# --- Required ---
options.platform_name = "iOS"
options.automation_name = "XCUITest"
options.device_name = "iPhone 15"            # Simulator name or real device name
options.platform_version = "17.0"            # iOS version

# --- App ---
options.app = "./apps/MyApp.app"             # .app for simulator, .ipa for device

# --- App state ---
options.no_reset = False
options.full_reset = False

# --- Real device only ---
options.set_capability("appium:udid", "auto")               # Auto-detect connected device
options.set_capability("appium:xcodeOrgId", "TEAM_ID")      # Apple Developer Team ID
options.set_capability("appium:xcodeSigningId", "iPhone Developer")

# --- WebView / Safari ---
options.set_capability("appium:includeSafariInWebviews", True)
options.set_capability("appium:webviewConnectTimeout", 30000)

# --- Performance ---
options.set_capability("appium:useNewWDA", False)            # Reuse existing WDA
options.set_capability("appium:wdaStartupRetries", 3)
```

**iOS-specific notes:**

- `platformVersion` is required for iOS (not required for Android)
- Simulator vs real device: simulators use `.app` bundles, real devices use signed `.ipa` files
- Real devices need code signing capabilities (`xcodeOrgId`, `xcodeSigningId`)
- iOS testing requires macOS + Xcode. You cannot run iOS tests from Windows or Linux.

---

## 3. React Native-Specific Capabilities

React Native apps render native components, so you use standard Android/iOS capabilities plus these additions:

```python
# Android - React Native additions
options.set_capability("appium:ensureWebviewsHavePages", True)
options.set_capability("appium:nativeWebScreenshot", True)

# iOS - React Native additions
options.set_capability("appium:webviewConnectTimeout", 30000)
```

**React Native context handling:**

Most React Native UI stays in NATIVE_APP context. WebViews appear when the app uses `react-native-webview` for embedded web content.

```python
# Check contexts
contexts = driver.contexts  # ['NATIVE_APP', 'WEBVIEW_com.myapp']

# Switch if needed
driver.switch_to.context('WEBVIEW_com.myapp')
# ... interact with web elements using CSS/id locators ...
driver.switch_to.context('NATIVE_APP')
```

---

## 4. Flutter-Specific Capabilities

Flutter apps need a different driver or the Appium Flutter integration.

**Option A: Use Appium with UiAutomator2/XCUITest (simpler)**

Works out of the box but elements are harder to locate because Flutter renders its own widget tree, not native Views.

```python
# Same capabilities as standard Android/iOS
# But locators will be less intuitive
# Use Appium Inspector to find the rendered accessibility labels
```

**Option B: Use Appium Flutter Driver (better locators)**

```bash
appium driver install --source=npm appium-flutter-driver
```

```python
options.automation_name = "Flutter"
options.set_capability("appium:retryBackoffTime", 500)

# Flutter-specific locators
driver.find_element(AppiumBy.FLUTTER_INTEGRATION, "key_login_button")
```

**Recommendation:** Start with Option A (standard driver). It works for most UI testing. Move to Option B if you need to interact with elements deep in the Flutter widget tree that are not exposed as accessible.

---

## 5. Device Cloud Capabilities

### BrowserStack

```python
def get_browserstack_options(device_config):
    """Build BrowserStack capabilities."""
    options = UiAutomator2Options()  # or XCUITestOptions for iOS
    options.platform_name = device_config["platform"]
    options.set_capability("bstack:options", {
        "userName": os.getenv("BROWSERSTACK_USERNAME"),
        "accessKey": os.getenv("BROWSERSTACK_ACCESS_KEY"),
        "appUrl": os.getenv("BROWSERSTACK_APP_URL"),
        "deviceName": device_config["device"],
        "osVersion": device_config["os_version"],
        "projectName": "MyApp Tests",
        "buildName": f"Regression-{datetime.now().strftime('%Y%m%d')}",
        "sessionName": device_config["device"],
        "debug": True,
        "networkLogs": True,
    })
    return options

# Server URL for BrowserStack
APPIUM_SERVER = "https://hub-cloud.browserstack.com/wd/hub"
```

### Sauce Labs

```python
options.set_capability("sauce:options", {
    "username": os.getenv("SAUCE_USERNAME"),
    "accessKey": os.getenv("SAUCE_ACCESS_KEY"),
    "appiumVersion": "2.0",
    "build": f"Regression-{datetime.now().strftime('%Y%m%d')}",
    "name": "Login Tests",
})

# Server URL for Sauce Labs
APPIUM_SERVER = "https://ondemand.us-west-1.saucelabs.com:443/wd/hub"
```

### AWS Device Farm

```python
# AWS Device Farm uses standard capabilities
# The app URL is an S3 presigned URL from the Device Farm API
options.app = os.getenv("AWS_APP_URL")  # Upload via AWS SDK first

# Server URL from Device Farm project
APPIUM_SERVER = os.getenv("AWS_DEVICE_FARM_URL")
```

---

## 6. Environment Variable Pattern

Never hardcode credentials, device names, or app paths. Use environment variables with sensible defaults:

```python
import os

# Required (fail fast if missing)
def require_env(key):
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Required environment variable '{key}' is not set")
    return value

# Optional with defaults
APPIUM_SERVER = os.getenv("APPIUM_SERVER", "http://localhost:4723")
TEST_PLATFORM = os.getenv("TEST_PLATFORM", "android")
ANDROID_DEVICE = os.getenv("ANDROID_DEVICE", "emulator-5554")
ANDROID_APP = os.getenv("ANDROID_APP_PATH", "./apps/app-debug.apk")
IOS_DEVICE = os.getenv("IOS_DEVICE", "iPhone 15")
IOS_VERSION = os.getenv("IOS_VERSION", "17.0")
IOS_APP = os.getenv("IOS_APP_PATH", "./apps/MyApp.app")

# Cloud credentials (required only for cloud runs)
BS_USERNAME = os.getenv("BROWSERSTACK_USERNAME", "")
BS_ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY", "")
```

**Running tests with different configs:**

```bash
# Local Android emulator (default)
pytest tests/

# Local iOS simulator
TEST_PLATFORM=ios pytest tests/

# BrowserStack
TEST_PLATFORM=android \
APPIUM_SERVER=https://hub-cloud.browserstack.com/wd/hub \
BROWSERSTACK_USERNAME=user \
BROWSERSTACK_ACCESS_KEY=key \
BROWSERSTACK_APP_URL=bs://app-id \
pytest tests/
```
