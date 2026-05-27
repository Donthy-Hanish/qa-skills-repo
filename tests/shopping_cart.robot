*** Settings ***
Documentation     BDD Test Cases for Shopping Cart - Add Items & Real-Time Total Update.
...               This file contains stubbed-out test cases mapped to the generated scenarios TC-001 through TC-018.
Library           SeleniumLibrary

*** Variables ***
${URL}            https://example.com
${BROWSER}        Chrome

*** Test Cases ***
# --- POSITIVE TEST SCENARIOS ---

TC-001: Add a single in-stock item to cart
    [Documentation]    Verify cart total updates after adding one item
    [Tags]    positive    critical    cart    add-item
    Given the user is logged in and on a product page for "Wireless Mouse"
    And the product is in stock
    When the user clicks the "Add to Cart" button
    Then the cart icon badge should update to show "1"
    And the cart total should display the item price "₹1,299.00"
    And a confirmation message "Item added to cart" should appear

TC-002: Add multiple different items and verify cumulative total
    [Documentation]    Cart total must sum all added items in real time
    [Tags]    positive    critical    cart    real-time-update
    Given the user is logged in and has added "Wireless Mouse" (₹1,299.00) to the cart
    When the user navigates to the product page for "USB Keyboard"
    And the user clicks the "Add to Cart" button
    Then the cart badge should show "2"
    And the cart total should display "₹2,798.00"
    And the total should update without requiring a page reload

TC-003: Increase item quantity and verify total update
    [Documentation]    Changing quantity must trigger immediate total recalculation
    [Tags]    positive    high    cart    quantity-update
    Given the user is logged in and has "Wireless Mouse" (₹1,299.00) in the cart
    When the user opens the cart and increases the quantity to "3"
    Then the line item total should display "₹3,897.00"
    And the cart total should update to "₹3,897.00" in real time

TC-004: Add same item twice — quantity consolidates
    [Documentation]    Duplicate add should increment qty, not create a new line
    [Tags]    positive    high    cart    deduplication
    Given the user is logged in and has "Wireless Mouse" in the cart with quantity "1"
    When the user clicks "Add to Cart" again on the same product page
    Then the cart should show "Wireless Mouse" with quantity "2"
    And the cart total should reflect the updated quantity price
    And there should be only one line item for "Wireless Mouse"

TC-005: Cart persists after navigating away and returning
    [Documentation]    Cart state must be preserved during same-session navigation
    [Tags]    positive    medium    cart    persistence
    Given the user is logged in and has items in the cart totalling "₹2,798.00"
    When the user navigates to the home page
    And the user navigates back to the cart page
    Then the cart should still contain all previously added items
    And the cart total should still display "₹2,798.00"

# --- NEGATIVE TEST SCENARIOS ---

TC-006: Guest user cannot add items to cart
    [Documentation]    Unauthenticated users must be prompted to log in
    [Tags]    negative    critical    cart    authentication
    Given the user is not logged in
    And the user is on a product page for "Wireless Mouse"
    When the user clicks the "Add to Cart" button
    Then the user should be redirected to the login page
    And the cart should remain empty

TC-007: Add an out-of-stock item
    [Documentation]    Disabled Add to Cart prevents adding unavailable stock
    [Tags]    negative    high    cart    inventory
    Given the user is logged in
    And the product "Wireless Mouse" is out of stock
    When the user views the product page
    Then the "Add to Cart" button should be disabled or replaced with "Out of Stock"
    And the user should not be able to add the item to the cart

TC-008: Add item with quantity exceeding available stock
    [Documentation]    Stock limit must prevent over-ordering with clear messaging
    [Tags]    negative    high    cart    stock-limit
    Given the user is logged in
    And the product "Wireless Mouse" has only "3" units in stock
    When the user attempts to set quantity to "10" and clicks "Add to Cart"
    Then the system should show an error "Only 3 items available"
    And the cart quantity should be capped at "3"
    And the cart total should reflect the capped quantity

TC-009: Cart total does not update when item addition fails
    [Documentation]    Failed API response must not corrupt the cart state
    [Tags]    negative    high    cart    api-error    error-handling
    Given the user is logged in and the cart total is "₹1,299.00"
    And the add-to-cart API is returning a 500 error
    When the user attempts to add "USB Keyboard" to the cart
    Then the cart total should remain "₹1,299.00"
    And an error message "Failed to add item. Please try again." should appear
    And the cart badge count should not change

TC-010: Removed item reflects immediately in cart total
    [Documentation]    Removal must trigger the same real-time total update as addition
    [Tags]    negative    medium    cart    remove-item
    Given the user is logged in and the cart contains "Wireless Mouse" (₹1,299.00) and "USB Keyboard" (₹1,499.00)
    And the cart total displays "₹2,798.00"
    When the user removes "Wireless Mouse" from the cart
    Then the cart total should update to "₹1,499.00" in real time
    And the cart should only show "USB Keyboard"

# --- BOUNDARY TEST SCENARIOS ---

TC-011: Add exactly 1 item (minimum quantity)
    [Documentation]    Verify cart behavior at lower boundary (qty = 1)
    [Tags]    boundary    high    cart    quantity
    Given the user is logged in and the cart is empty
    When the user adds "1" unit of "Wireless Mouse" (₹1,299.00)
    Then the cart badge should show "1"
    And the cart total should display exactly "₹1,299.00"
    And no error or warning should appear

TC-012: Add maximum allowed quantity per item
    [Documentation]    Verify cart behavior at upper boundary (qty = 99)
    [Tags]    boundary    critical    cart    quantity-max
    Given the user is logged in and the cart is empty
    And the maximum order quantity per item is "99"
    When the user sets the quantity to "99" and adds "Wireless Mouse" (₹1,299.00)
    Then the cart should accept the quantity of "99"
    And the cart total should display "₹1,28,601.00"
    And no error should appear

TC-013: Set quantity to 0 — item should be removed
    [Documentation]    Setting quantity to zero is a boundary removal trigger
    [Tags]    boundary    high    cart    quantity-zero
    Given the user is logged in and the cart contains "Wireless Mouse" with quantity "1"
    When the user sets the item quantity to "0" in the cart
    Then the item should be removed from the cart
    And the cart total should update to "₹0.00" or show "Your cart is empty"

TC-014: Cart total with high-value precision (decimal handling)
    [Documentation]    Validate that float precision issues do not corrupt cart calculations
    [Tags]    boundary    medium    cart    decimal    pricing
    Given the user is logged in and the cart is empty
    When the user adds "3" units of "Premium Cable" priced at "₹99.99" each
    Then the cart total should display "₹299.97"
    And the total should not be rounded incorrectly to "₹300.00"

# --- EDGE CASE SCENARIOS ---

TC-015: Real-time update during slow network (latency simulation)
    [Documentation]    Network throttling must not lead to double additions or state errors
    [Tags]    edge-case    critical    cart    network    performance
    Given the user is logged in and on a product page
    And the network connection is throttled to slow 3G
    When the user clicks "Add to Cart"
    Then a loading indicator should appear on the cart icon
    And the cart total should update once the server responds
    And the update should complete within "5 seconds"
    And no duplicate item should be added if the user clicks again while loading

TC-016: Add item from multiple browser tabs simultaneously
    [Documentation]    Validate cart state synchronization when interacting on multiple tabs
    [Tags]    edge-case    high    cart    multi-tab    session
    Given the user is logged in and has the cart open in "Tab A" and a product page in "Tab B"
    When the user adds "Wireless Mouse" to the cart from "Tab B"
    Then switching to "Tab A" and refreshing should show the updated cart total
    And the total should reflect the item added from Tab B

TC-017: Session expires mid-cart interaction
    [Documentation]    Session expiration should route to login and restore state afterward
    [Tags]    edge-case    medium    cart    session    authentication
    Given the user is logged in and has items in the cart
    And the user's session expires due to inactivity
    When the user attempts to add another item to the cart
    Then the system should prompt the user to log in again
    And after re-login, the cart should be restored to its previous state
    And the new item should be added successfully

TC-018: Product price changes between add and checkout
    [Documentation]    Admin price updates during checkout phase must prompt user correctly
    [Tags]    edge-case    low    cart    pricing    consistency
    Given the user has "Wireless Mouse" in the cart at "₹1,299.00"
    When an admin updates the price of "Wireless Mouse" to "₹1,499.00"
    And the user proceeds to checkout
    Then the cart should display the updated price "₹1,499.00"
    And a notice "Price has been updated" should inform the user
    And the cart total should reflect the new price


*** Keywords ***
# --- Placeholder Keyword Implementations (To be developed in Python/SeleniumLibrary) ---

the user is logged in and on a product page for "${product}"
    [Documentation]    Stub keyword.
    No Operation

the product is in stock
    [Documentation]    Stub keyword.
    No Operation

the user clicks the "Add to Cart" button
    [Documentation]    Stub keyword.
    No Operation

the cart icon badge should update to show "${count}"
    [Documentation]    Stub keyword.
    No Operation

the cart total should display the item price "${price}"
    [Documentation]    Stub keyword.
    No Operation

a confirmation message "${message}" should appear
    [Documentation]    Stub keyword.
    No Operation

the user is logged in and has added "${product}" (${price}) to the cart
    [Documentation]    Stub keyword.
    No Operation

the user navigates to the product page for "${product}"
    [Documentation]    Stub keyword.
    No Operation

the cart badge should show "${count}"
    [Documentation]    Stub keyword.
    No Operation

the cart total should display "${total}"
    [Documentation]    Stub keyword.
    No Operation

the total should update without requiring a page reload
    [Documentation]    Stub keyword.
    No Operation

the user is logged in and has "${product}" (${price}) in the cart
    [Documentation]    Stub keyword.
    No Operation

the user opens the cart and increases the quantity to "${qty}"
    [Documentation]    Stub keyword.
    No Operation

the line item total should display "${total}"
    [Documentation]    Stub keyword.
    No Operation

the cart total should update to "${total}" in real time
    [Documentation]    Stub keyword.
    No Operation

the user is logged in and has "${product}" in the cart with quantity "${qty}"
    [Documentation]    Stub keyword.
    No Operation

the user clicks "Add to Cart" again on the same product page
    [Documentation]    Stub keyword.
    No Operation

the cart should show "${product}" with quantity "${qty}"
    [Documentation]    Stub keyword.
    No Operation

the cart total should reflect the updated quantity price
    [Documentation]    Stub keyword.
    No Operation

the should be only one line item for "${product}"
    [Documentation]    Stub keyword.
    No Operation

the user is logged in and has items in the cart totalling "${total}"
    [Documentation]    Stub keyword.
    No Operation

the user navigates to the home page
    [Documentation]    Stub keyword.
    No Operation

the user navigates back to the cart page
    [Documentation]    Stub keyword.
    No Operation

the cart should still contain all previously added items
    [Documentation]    Stub keyword.
    No Operation

the cart total should still display "${total}"
    [Documentation]    Stub keyword.
    No Operation

the user is not logged in
    [Documentation]    Stub keyword.
    No Operation

the user is on a product page for "${product}"
    [Documentation]    Stub keyword.
    No Operation

the user should be redirected to the login page
    [Documentation]    Stub keyword.
    No Operation

the cart should remain empty
    [Documentation]    Stub keyword.
    No Operation

the user is logged in
    [Documentation]    Stub keyword.
    No Operation

the product "${product}" is out of stock
    [Documentation]    Stub keyword.
    No Operation

the user views the product page
    [Documentation]    Stub keyword.
    No Operation

the "Add to Cart" button should be disabled or replaced with "Out of Stock"
    [Documentation]    Stub keyword.
    No Operation

the user should not be able to add the item to the cart
    [Documentation]    Stub keyword.
    No Operation

the product "${product}" has only "${count}" units in stock
    [Documentation]    Stub keyword.
    No Operation

the user attempts to set quantity to "${qty}" and clicks "Add to Cart"
    [Documentation]    Stub keyword.
    No Operation

the system should show an error "${message}"
    [Documentation]    Stub keyword.
    No Operation

the cart quantity should be capped at "${qty}"
    [Documentation]    Stub keyword.
    No Operation

the cart total should reflect the capped quantity
    [Documentation]    Stub keyword.
    No Operation

the user is logged in and the cart total is "${total}"
    [Documentation]    Stub keyword.
    No Operation

the add-to-cart API is returning a 500 error
    [Documentation]    Stub keyword.
    No Operation

the user attempts to add "${product}" to the cart
    [Documentation]    Stub keyword.
    No Operation

the cart total should remain "${total}"
    [Documentation]    Stub keyword.
    No Operation

an error message "${message}" should appear
    [Documentation]    Stub keyword.
    No Operation

the cart badge count should not change
    [Documentation]    Stub keyword.
    No Operation

the user is logged in and the cart contains "${product1}" (${price1}) and "${product2}" (${price2})
    [Documentation]    Stub keyword.
    No Operation

the cart total displays "${total}"
    [Documentation]    Stub keyword.
    No Operation

the user removes "${product}" from the cart
    [Documentation]    Stub keyword.
    No Operation

the cart should only show "${product}"
    [Documentation]    Stub keyword.
    No Operation

the user is logged in and the cart is empty
    [Documentation]    Stub keyword.
    No Operation

the user adds "${qty}" unit of "${product}" (${price})
    [Documentation]    Stub keyword.
    No Operation

the user adds "${qty}" units of "${product}" (${price})
    [Documentation]    Stub keyword.
    No Operation

the user sets the quantity to "${qty}" and adds "${product}" (${price})
    [Documentation]    Stub keyword.
    No Operation

the maximum order quantity per item is "${qty}"
    [Documentation]    Stub keyword.
    No Operation

the cart should accept the quantity of "${qty}"
    [Documentation]    Stub keyword.
    No Operation

the user sets the item quantity to "${qty}" in the cart
    [Documentation]    Stub keyword.
    No Operation

the item should be removed from the cart
    [Documentation]    Stub keyword.
    No Operation

the cart total should update to "${total}" or show "Your cart is empty"
    [Documentation]    Stub keyword.
    No Operation

the user adds "${qty}" units of "${product}" priced at "${price}" each
    [Documentation]    Stub keyword.
    No Operation

the total should not be rounded incorrectly to "${total}"
    [Documentation]    Stub keyword.
    No Operation

the user is logged in and on a product page
    [Documentation]    Stub keyword.
    No Operation

the network connection is throttled to slow 3G
    [Documentation]    Stub keyword.
    No Operation

the user clicks "Add to Cart"
    [Documentation]    Stub keyword.
    No Operation

a loading indicator should appear on the cart icon
    [Documentation]    Stub keyword.
    No Operation

the cart total should update once the server responds
    [Documentation]    Stub keyword.
    No Operation

the update should complete within "${time}"
    [Documentation]    Stub keyword.
    No Operation

no duplicate item should be added if the user clicks again while loading
    [Documentation]    Stub keyword.
    No Operation

the user is logged in and has the cart open in "${tabA}" and a product page in "${tabB}"
    [Documentation]    Stub keyword.
    No Operation

the user adds "${product}" to the cart from "${tab}"
    [Documentation]    Stub keyword.
    No Operation

switching to "${tab}" and refreshing should show the updated cart total
    [Documentation]    Stub keyword.
    No Operation

the total should reflect the item added from ${tab}
    [Documentation]    Stub keyword.
    No Operation

the user is logged in and has items in the cart
    [Documentation]    Stub keyword.
    No Operation

the user's session expires due to inactivity
    [Documentation]    Stub keyword.
    No Operation

the user attempts to add another item to the cart
    [Documentation]    Stub keyword.
    No Operation

the system should prompt the user to log in again
    [Documentation]    Stub keyword.
    No Operation

after re-login, the cart should be restored to its previous state
    [Documentation]    Stub keyword.
    No Operation

the new item should be added successfully
    [Documentation]    Stub keyword.
    No Operation

the user has "${product}" in the cart at "${price}"
    [Documentation]    Stub keyword.
    No Operation

an admin updates the price of "${product}" to "${price}"
    [Documentation]    Stub keyword.
    No Operation

the user proceeds to checkout
    [Documentation]    Stub keyword.
    No Operation

the cart should display the updated price "${price}"
    [Documentation]    Stub keyword.
    No Operation

a notice "${message}" should inform the user
    [Documentation]    Stub keyword.
    No Operation

no error or warning should appear
    [Documentation]    Stub keyword.
    No Operation
