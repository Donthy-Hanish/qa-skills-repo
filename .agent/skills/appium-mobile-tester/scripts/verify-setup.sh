#!/usr/bin/env bash
# verify-setup.sh - Verify Appium mobile testing environment
# Run this before your first test or when "Could not start session" errors appear.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0

check_pass() {
    echo -e "  ${GREEN}[PASS]${NC} $1"
    ((PASS++))
}

check_fail() {
    echo -e "  ${RED}[FAIL]${NC} $1"
    ((FAIL++))
}

check_warn() {
    echo -e "  ${YELLOW}[WARN]${NC} $1"
    ((WARN++))
}

echo "========================================"
echo "Appium Mobile Testing - Setup Verifier"
echo "========================================"
echo ""

# --- Python ---
echo "1. Python"
if command -v python3 &> /dev/null; then
    PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
    PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 9 ]; then
        check_pass "Python $PY_VER (>= 3.9 required)"
    else
        check_fail "Python $PY_VER found but >= 3.9 required"
    fi
else
    check_fail "Python 3 not found. Install Python 3.9+"
fi

# --- Python packages ---
echo ""
echo "2. Python Packages"
for pkg in "Appium-Python-Client" "pytest" "pytest-html" "selenium"; do
    if python3 -c "import importlib; importlib.import_module('${pkg//-/_}'.lower().split('-')[0])" 2>/dev/null || \
       python3 -m pip show "$pkg" &>/dev/null; then
        PKG_VER=$(python3 -m pip show "$pkg" 2>/dev/null | grep "^Version:" | awk '{print $2}')
        check_pass "$pkg ($PKG_VER)"
    else
        check_fail "$pkg not installed. Run: pip install $pkg"
    fi
done

# --- Node.js ---
echo ""
echo "3. Node.js"
if command -v node &> /dev/null; then
    NODE_VER=$(node --version)
    check_pass "Node.js $NODE_VER"
else
    check_fail "Node.js not found. Install Node.js 18+ from https://nodejs.org"
fi

# --- Appium Server ---
echo ""
echo "4. Appium Server"
if command -v appium &> /dev/null; then
    APPIUM_VER=$(appium --version 2>&1)
    check_pass "Appium $APPIUM_VER"

    # Check installed drivers
    echo ""
    echo "5. Appium Drivers"
    DRIVERS=$(appium driver list --installed 2>&1)

    if echo "$DRIVERS" | grep -qi "uiautomator2"; then
        check_pass "UiAutomator2 driver installed"
    else
        check_fail "UiAutomator2 driver missing. Run: appium driver install uiautomator2"
    fi

    if echo "$DRIVERS" | grep -qi "xcuitest"; then
        check_pass "XCUITest driver installed"
    else
        if [[ "$OSTYPE" == "darwin"* ]]; then
            check_fail "XCUITest driver missing. Run: appium driver install xcuitest"
        else
            check_warn "XCUITest driver not installed (iOS testing requires macOS)"
        fi
    fi
else
    check_fail "Appium not found. Run: npm install -g appium"
    echo ""
    echo "5. Appium Drivers"
    check_fail "Skipped (Appium not installed)"
fi

# --- Android SDK ---
echo ""
echo "6. Android SDK"
if [ -n "$ANDROID_HOME" ]; then
    check_pass "ANDROID_HOME set to $ANDROID_HOME"
else
    check_fail "ANDROID_HOME not set. Set it to your Android SDK path."
fi

if command -v adb &> /dev/null; then
    ADB_VER=$(adb version 2>&1 | head -1)
    check_pass "ADB available: $ADB_VER"

    # Check connected devices
    echo ""
    echo "7. Connected Android Devices/Emulators"
    DEVICES=$(adb devices 2>/dev/null | grep -v "^List" | grep -v "^$" | grep -v "^adb")
    if [ -n "$DEVICES" ]; then
        while IFS= read -r line; do
            DEVICE_ID=$(echo "$line" | awk '{print $1}')
            DEVICE_STATUS=$(echo "$line" | awk '{print $2}')
            if [ "$DEVICE_STATUS" = "device" ]; then
                check_pass "Device: $DEVICE_ID (connected)"
            elif [ "$DEVICE_STATUS" = "offline" ]; then
                check_warn "Device: $DEVICE_ID (offline)"
            else
                check_warn "Device: $DEVICE_ID ($DEVICE_STATUS)"
            fi
        done <<< "$DEVICES"
    else
        check_warn "No Android devices/emulators connected. Start one via Android Studio AVD Manager."
    fi
else
    check_fail "ADB not found. Install Android SDK Platform Tools."
    echo ""
    echo "7. Connected Android Devices/Emulators"
    check_fail "Skipped (ADB not installed)"
fi

# --- Java ---
echo ""
echo "8. Java"
if [ -n "$JAVA_HOME" ]; then
    check_pass "JAVA_HOME set to $JAVA_HOME"
else
    check_warn "JAVA_HOME not set. Some Android tools may need it."
fi

if command -v java &> /dev/null; then
    JAVA_VER=$(java -version 2>&1 | head -1)
    check_pass "Java available: $JAVA_VER"
else
    check_warn "Java not found. Android SDK tools may need JDK 11+."
fi

# --- iOS (macOS only) ---
echo ""
echo "9. iOS Testing (macOS only)"
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v xcrun &> /dev/null; then
        XCODE_VER=$(xcodebuild -version 2>/dev/null | head -1)
        check_pass "Xcode: $XCODE_VER"

        SIM_COUNT=$(xcrun simctl list devices available 2>/dev/null | grep -c "iPhone\|iPad" || true)
        if [ "$SIM_COUNT" -gt 0 ]; then
            check_pass "$SIM_COUNT iOS simulators available"
        else
            check_warn "No iOS simulators found. Create one in Xcode > Window > Devices and Simulators."
        fi
    else
        check_fail "Xcode command line tools not found. Run: xcode-select --install"
    fi
else
    check_warn "Not macOS - iOS testing not available on this platform."
fi

# --- Appium Server Running ---
echo ""
echo "10. Appium Server Status"
if curl -s http://localhost:4723/status &>/dev/null; then
    check_pass "Appium server running on http://localhost:4723"
else
    check_warn "Appium server not running on default port 4723. Start with: appium"
fi

# --- Summary ---
echo ""
echo "========================================"
echo "Summary: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}, ${YELLOW}$WARN warnings${NC}"
echo "========================================"

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}Fix the failures above before running tests.${NC}"
    exit 1
else
    echo -e "${GREEN}Environment looks good. You can run tests.${NC}"
    exit 0
fi
