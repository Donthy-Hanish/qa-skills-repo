"""
<module_name>.py — Custom keyword library for Robot Framework.

Provides utility keywords for <describe purpose>.
Import in .robot files via:  Library    libraries/<module_name>.py
"""

import random
import string
from datetime import datetime, timedelta
from robot.api.deco import keyword


class <ClassName>:
    """Robot Framework custom keyword library for <purpose>."""

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    @keyword("Generate Random Email")
    def generate_random_email(self, domain="example.com"):
        """Generate a unique random email address for test data.

        Example:
            ${email}=    Generate Random Email    testdomain.com
        """
        prefix = ''.join(random.choices(string.ascii_lowercase, k=8))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"test_{prefix}_{timestamp}@{domain}"

    @keyword("Generate Test User Data")
    def generate_test_user_data(self, role="member"):
        """Generate a dictionary of test user data.

        Args:
            role: User role — 'admin', 'member', or 'guest'.

        Returns:
            dict with name, email, password, role fields.
        """
        email = self.generate_random_email()
        return {
            "name": f"Test User {random.randint(1000, 9999)}",
            "email": email,
            "password": "SecureP@ss123!",
            "role": role
        }

    @keyword("Calculate Expected Total")
    def calculate_expected_total(self, items):
        """Sum item prices for cart total verification.

        Args:
            items: List of dicts with 'price' and 'quantity' keys.

        Returns:
            Formatted total string like '₹1,299.00'.
        """
        total = sum(
            float(item["price"]) * int(item["quantity"])
            for item in items
        )
        return f"₹{total:,.2f}"
