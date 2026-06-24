# Locator Strategy Guide

## Table of Contents

1. The Locator Resilience Pyramid
2. accessibility_id - The Cross-Platform Winner
3. resource-id (Android) and name (iOS)
4. XPath - When You Have No Other Choice
5. iOS-Specific: Class Chain and Predicate String
6. React Native testID Mapping
7. Building Locators with Appium Inspector
8. Multi-Strategy Fallback Chains
9. Working with Developers to Add Testability

---

## 1. The Locator Resilience Pyramid

From most to least resilient:

```
        accessibility_id
       (cross-platform, stable)
      -------------------------
         resource-id / name
       (platform-specific, stable)
      -------------------------
      class chain / predicate string
        (iOS only, good stability)
      -------------------------
              XPath
       (fragile, slow, last resort)
```

Always start at the top. Only move down when the strategy above is not available for a given element.

---

## 2. accessibility_id - The Cross-Platform Winner

**What it maps to:**
- Android: `content-description` attribute
- iOS: `accessibilityIdentifier` property
- React Native: `testID` prop (automatically maps to both platforms)

**Why it is the best:**
- Same locator value works on both Android and iOS
- Not affected by UI hierarchy changes
- Not affected by text localization (button says "Login" in English, "Connexion" in French, but accessibility_id stays "login-button")
- Stable across app updates unless deliberately changed

**How to use in Python:**

```python
from appium.webdriver.common.appiumby import AppiumBy

element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "login-button")
```

**How React Native devs set it:**

```jsx
<TouchableOpacity testID="login-button" onPress={handleLogin}>
  <Text>Login</Text>
</TouchableOpacity>
```

**Limitation:** Not every element has an accessibility_id. If devs have not set testID/accessibilityLabel, this strategy will not find the element. That is why you need the fallback chain.

---

## 3. resource-id (Android) and name (iOS)

**Android resource-id:**
- Set by the developer in XML layout or programmatically
- Format: `com.package.name:id/element_id`
- You can use the short form in some cases: just `element_id`

```python
# Full resource-id
element = driver.find_element(AppiumBy.ID, "com.myapp.prolink:id/email_input")

# Short form (sometimes works, depends on driver version)
element = driver.find_element(AppiumBy.ID, "email_input")
```

**iOS name:**
- Maps to the `name` or `label` attribute
- Often matches the visible text, which means it breaks with localization

```python
element = driver.find_element(AppiumBy.NAME, "Login")
```

**When to use:** As the second strategy in the fallback chain when accessibility_id is not set.

---

## 4. XPath - When You Have No Other Choice

XPath works on both platforms but is the least desirable strategy.

**Why XPath is problematic on mobile:**
- Slow. Appium has to traverse the entire element tree.
- Fragile. Any hierarchy change (a new wrapper view, reordered children) breaks it.
- Different between platforms. Android and iOS have completely different element trees for the same React Native screen.

**When you must use XPath:**
- Element has no accessibility_id, no resource-id, and no unique name
- You need to find an element by visible text as a last resort
- You need to find an element relative to another element (parent/sibling)

**XPath patterns for mobile:**

```python
# By text content (fragile but sometimes necessary)
driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Welcome']")

# By partial text
driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Welcome')]")

# By index (very fragile)
driver.find_element(AppiumBy.XPATH, "(//android.widget.EditText)[1]")

# Relative (find button inside a specific container)
driver.find_element(AppiumBy.XPATH, "//android.view.ViewGroup[@content-desc='login-form']//android.widget.Button")
```

**Rule:** If you find yourself writing complex XPath for many elements, stop and talk to the dev team about adding testIDs.

---

## 5. iOS-Specific: Class Chain and Predicate String

These are faster and more stable alternatives to XPath on iOS.

**-ios class chain:**

Similar to XPath but uses iOS class names and is faster.

```python
# Direct child
driver.find_element(AppiumBy.IOS_CLASS_CHAIN,
    "**/XCUIElementTypeButton[`label == 'Login'`]")

# Nested
driver.find_element(AppiumBy.IOS_CLASS_CHAIN,
    "**/XCUIElementTypeCell/XCUIElementTypeButton[`label == 'Delete'`]")
```

**-ios predicate string:**

Filter elements by attributes using NSPredicate syntax.

```python
# By label
driver.find_element(AppiumBy.IOS_PREDICATE,
    "type == 'XCUIElementTypeButton' AND label == 'Login'")

# Partial match
driver.find_element(AppiumBy.IOS_PREDICATE,
    "type == 'XCUIElementTypeStaticText' AND label CONTAINS 'Welcome'")

# Multiple conditions
driver.find_element(AppiumBy.IOS_PREDICATE,
    "type == 'XCUIElementTypeTextField' AND visible == true AND enabled == true")
```

These do not work on Android. Use them only in iOS-specific locator entries in the fallback chain.

---

## 6. React Native testID Mapping

React Native maps `testID` differently on each platform:

| React Native | Android result | iOS result |
|---|---|---|
| `testID="login-btn"` | `content-desc="login-btn"` | `accessibilityIdentifier="login-btn"` |
| `accessibilityLabel="Login Button"` | `content-desc="Login Button"` | `accessibilityLabel="Login Button"` |

**Best practice for React Native:**
- Use `testID` for test automation (stable, not visible to users)
- Use `accessibilityLabel` for screen reader support (visible to assistive tech)
- Do not use `accessibilityLabel` as your locator - it may change with UX updates

**Finding elements in React Native apps:**
- React Native renders native components, so use the same Appium locators
- The element tree shows Android Views or iOS UIKit elements, not React components
- A React Native `<View>` becomes `android.view.ViewGroup` on Android and `XCUIElementTypeOther` on iOS

---

## 7. Building Locators with Appium Inspector

Step-by-step workflow for building locators for a new screen:

1. Start Appium server: `appium`
2. Open Appium Inspector, paste capabilities, start session
3. Navigate to the target screen in the app
4. Click the element you want to locate
5. Check the attributes panel on the right:
   - Look for `content-desc` (Android) or `accessibilityIdentifier` (iOS) first
   - If found, that is your accessibility_id
   - If not, check `resource-id` (Android) or `name` (iOS)
   - If neither, note the class name and visible text for XPath
6. Test your locator using the Search bar in Inspector
7. Record the locator in your Page Object's LOCATORS dict

**Tip:** Screenshot each screen from Appium Inspector and save it alongside your Page Object file. This makes it easy to update locators when the UI changes.

---

## 8. Multi-Strategy Fallback Chains

The skill's core self-healing mechanism. For every element, define multiple strategies in order of resilience:

```python
LOCATORS = {
    "submit_button": [
        # Strategy 1: accessibility_id (best)
        (AppiumBy.ACCESSIBILITY_ID, "submit-order"),
        # Strategy 2: resource-id (Android backup)
        (AppiumBy.ID, "com.myapp:id/btn_submit"),
        # Strategy 3: XPath (last resort)
        (AppiumBy.XPATH, "//android.widget.Button[@text='Submit Order']"),
    ],
}
```

The `find_element` method in the Page Object tries each strategy in order. If strategy 1 breaks (dev removed the testID), strategy 2 catches it. If strategy 2 breaks (dev renamed the resource-id), strategy 3 catches it.

**This is not magic self-healing.** It is a manual fallback chain that you build during test development. The advantage is:
- Tests do not break immediately when one locator changes
- You get time to fix the locator before the next strategy also breaks
- Failures tell you which strategy worked, so you know what shifted

---

## 9. Working with Developers to Add Testability

The highest-impact thing you can do for mobile test stability is get developers to add testIDs to their components.

**The ask is small:** Add a `testID` prop to interactive elements (buttons, inputs, links, cards). It takes 10 seconds per element and does not affect the user-visible UI.

**Template message for the dev team:**

```
Hey [dev name],

I am setting up Appium tests for [screen name]. To make the tests stable and
cross-platform, I need testID props on the interactive elements. Here is what
I need:

- [element 1] -> testID="screen-element-action" (e.g., "login-email-input")
- [element 2] -> testID="login-password-input"
- [element 3] -> testID="login-submit-button"
- [element 4] -> testID="login-forgot-password-link"

Naming convention: screen-element-action (kebab-case).

This does not affect the UI or accessibility labels. It just gives the test
framework a stable handle to find each element.
```

**Naming convention for testIDs:**
- Format: `screen-element-action` (kebab-case)
- Examples: `login-email-input`, `dashboard-search-field`, `settings-logout-button`
- Keep it descriptive and unique within the app
