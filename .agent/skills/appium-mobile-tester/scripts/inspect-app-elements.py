#!/usr/bin/env python3
"""
inspect-app-elements.py - Dump the current screen's element tree.

Use this when building Page Objects for a new screen to find
available locators (accessibility_id, resource-id, text, class).

Prerequisites:
  - Appium server running (default: http://localhost:4723)
  - App launched on device/emulator
  - An active Appium session OR provide capabilities to start one

Usage:
  # Connect to existing session (faster - use when Appium Inspector is open)
  python inspect-app-elements.py --session-id <session_id>

  # Start new session with Android defaults
  python inspect-app-elements.py --platform android --app ./apps/myapp.apk

  # Start new session with iOS defaults
  python inspect-app-elements.py --platform ios --app ./apps/MyApp.app

  # Save output to file
  python inspect-app-elements.py --platform android --app ./apps/myapp.apk --output elements.txt
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET

try:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    from appium.options.ios import XCUITestOptions
except ImportError:
    print("ERROR: Appium-Python-Client not installed.")
    print("Run: pip install Appium-Python-Client")
    sys.exit(1)


def get_driver(args):
    """Create or connect to an Appium session."""
    server = args.server or "http://localhost:4723"

    if args.platform == "android":
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.automation_name = "UiAutomator2"
        options.device_name = args.device or os.getenv("ANDROID_DEVICE", "emulator-5554")
        if args.app:
            options.app = args.app
        elif os.getenv("ANDROID_APP_PATH"):
            options.app = os.getenv("ANDROID_APP_PATH")
        options.no_reset = True  # Don't reset app state for inspection
    elif args.platform == "ios":
        options = XCUITestOptions()
        options.platform_name = "iOS"
        options.automation_name = "XCUITest"
        options.device_name = args.device or os.getenv("IOS_DEVICE", "iPhone 15")
        options.platform_version = os.getenv("IOS_VERSION", "17.0")
        if args.app:
            options.app = args.app
        elif os.getenv("IOS_APP_PATH"):
            options.app = os.getenv("IOS_APP_PATH")
        options.no_reset = True
    else:
        print(f"ERROR: Unknown platform '{args.platform}'. Use 'android' or 'ios'.")
        sys.exit(1)

    print(f"Connecting to Appium at {server}...")
    driver = webdriver.Remote(command_executor=server, options=options)
    return driver


def parse_element_tree(page_source, platform):
    """Parse page source XML and extract useful element info."""
    elements = []
    try:
        root = ET.fromstring(page_source)
    except ET.ParseError as e:
        print(f"ERROR parsing element tree: {e}")
        return elements

    for elem in root.iter():
        info = {}
        tag = elem.tag

        if platform == "android":
            info["class"] = tag
            info["text"] = elem.get("text", "")
            info["resource-id"] = elem.get("resource-id", "")
            info["content-desc"] = elem.get("content-desc", "")
            info["clickable"] = elem.get("clickable", "false")
            info["enabled"] = elem.get("enabled", "true")
            info["bounds"] = elem.get("bounds", "")
        elif platform == "ios":
            info["class"] = tag
            info["name"] = elem.get("name", "")
            info["label"] = elem.get("label", "")
            info["value"] = elem.get("value", "")
            info["type"] = elem.get("type", tag)
            info["enabled"] = elem.get("enabled", "true")
            info["visible"] = elem.get("visible", "true")

        # Only include elements with at least one useful attribute
        has_useful_attr = any([
            info.get("text"), info.get("resource-id"),
            info.get("content-desc"), info.get("name"),
            info.get("label"), info.get("value"),
        ])

        if has_useful_attr:
            elements.append(info)

    return elements


def suggest_locators(elements, platform):
    """Suggest locator strategies for interactive elements."""
    suggestions = []

    for elem in elements:
        locator_options = []

        if platform == "android":
            if elem.get("content-desc"):
                locator_options.append(
                    f'(AppiumBy.ACCESSIBILITY_ID, "{elem["content-desc"]}")'
                )
            if elem.get("resource-id"):
                locator_options.append(
                    f'(AppiumBy.ID, "{elem["resource-id"]}")'
                )
            if elem.get("text") and elem.get("clickable") == "true":
                locator_options.append(
                    f'(AppiumBy.XPATH, "//{elem["class"]}[@text=\'{elem["text"]}\']")'
                )
        elif platform == "ios":
            if elem.get("name"):
                locator_options.append(
                    f'(AppiumBy.ACCESSIBILITY_ID, "{elem["name"]}")'
                )
            if elem.get("label"):
                locator_options.append(
                    f'(AppiumBy.IOS_PREDICATE, "label == \'{elem["label"]}\'")'
                )

        if locator_options:
            desc = (
                elem.get("text") or elem.get("content-desc")
                or elem.get("name") or elem.get("label")
                or elem.get("resource-id") or elem.get("class")
            )
            suggestions.append({
                "description": desc[:50],
                "class": elem.get("class") or elem.get("type", "unknown"),
                "strategies": locator_options,
            })

    return suggestions


def main():
    parser = argparse.ArgumentParser(
        description="Inspect mobile app element tree for building Page Objects"
    )
    parser.add_argument(
        "--platform", choices=["android", "ios"], default="android",
        help="Target platform (default: android)"
    )
    parser.add_argument("--app", help="Path to app binary (.apk or .app)")
    parser.add_argument("--device", help="Device name or serial")
    parser.add_argument("--server", help="Appium server URL (default: http://localhost:4723)")
    parser.add_argument("--output", help="Save output to file instead of stdout")
    parser.add_argument(
        "--raw", action="store_true",
        help="Output raw page source XML instead of parsed elements"
    )
    args = parser.parse_args()

    driver = None
    try:
        driver = get_driver(args)
        print("Session started. Inspecting current screen...\n")

        page_source = driver.page_source

        if args.raw:
            output = page_source
        else:
            elements = parse_element_tree(page_source, args.platform)
            suggestions = suggest_locators(elements, args.platform)

            lines = []
            lines.append("=" * 60)
            lines.append(f"Screen Element Analysis ({args.platform.upper()})")
            lines.append(f"Total interactive elements found: {len(suggestions)}")
            lines.append("=" * 60)

            for i, s in enumerate(suggestions, 1):
                lines.append(f"\n--- Element {i}: {s['description']} ---")
                lines.append(f"  Class: {s['class']}")
                lines.append(f"  Suggested locators (best first):")
                for j, strategy in enumerate(s["strategies"], 1):
                    lines.append(f"    {j}. {strategy}")

            lines.append("\n" + "=" * 60)
            lines.append("Copy the locators above into your Page Object's LOCATORS dict.")
            lines.append("=" * 60)

            output = "\n".join(lines)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Output saved to {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        if driver:
            driver.quit()
            print("\nSession closed.")


if __name__ == "__main__":
    main()
