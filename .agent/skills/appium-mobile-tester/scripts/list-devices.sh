#!/usr/bin/env bash
# list-devices.sh - List all connected Android devices/emulators and iOS simulators
# Use to pick a device_name for your Appium capabilities.

echo "========================================"
echo "Connected Devices & Simulators"
echo "========================================"

# --- Android ---
echo ""
echo "--- Android Devices/Emulators ---"
if command -v adb &> /dev/null; then
    DEVICES=$(adb devices -l 2>/dev/null | grep -v "^List" | grep -v "^$" | grep -v "^adb")
    if [ -n "$DEVICES" ]; then
        echo "$DEVICES" | while IFS= read -r line; do
            SERIAL=$(echo "$line" | awk '{print $1}')
            STATUS=$(echo "$line" | awk '{print $2}')
            MODEL=$(echo "$line" | grep -o "model:[^ ]*" | cut -d: -f2)
            DEVICE=$(echo "$line" | grep -o "device:[^ ]*" | cut -d: -f2)
            echo "  Serial: $SERIAL"
            echo "  Status: $STATUS"
            [ -n "$MODEL" ] && echo "  Model:  $MODEL"
            [ -n "$DEVICE" ] && echo "  Device: $DEVICE"
            if [ "$STATUS" = "device" ]; then
                SDK=$(adb -s "$SERIAL" shell getprop ro.build.version.sdk 2>/dev/null)
                RELEASE=$(adb -s "$SERIAL" shell getprop ro.build.version.release 2>/dev/null)
                [ -n "$RELEASE" ] && echo "  Android: $RELEASE (API $SDK)"
            fi
            echo "  ---"
        done
    else
        echo "  No Android devices/emulators connected."
        echo "  Start an emulator via Android Studio AVD Manager,"
        echo "  or connect a device via USB with USB debugging enabled."
    fi
else
    echo "  ADB not found. Install Android SDK Platform Tools."
fi

# --- iOS (macOS only) ---
echo ""
echo "--- iOS Simulators ---"
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v xcrun &> /dev/null; then
        echo "  Available (booted marked with *):"
        xcrun simctl list devices available 2>/dev/null | grep -E "iPhone|iPad" | while IFS= read -r line; do
            if echo "$line" | grep -q "Booted"; then
                echo "  * $line"
            else
                echo "    $line"
            fi
        done
        echo ""
        echo "  To boot a simulator: xcrun simctl boot '<device_name>'"
        echo "  To list all (including unavailable): xcrun simctl list devices"
    else
        echo "  Xcode command line tools not found."
    fi
else
    echo "  iOS simulators require macOS + Xcode."
fi

echo ""
echo "========================================"
echo "Use the serial (Android) or device name (iOS) in your capabilities."
echo "========================================"
