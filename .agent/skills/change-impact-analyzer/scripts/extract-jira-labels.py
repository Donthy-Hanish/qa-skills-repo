#!/usr/bin/env python3
"""
extract-jira-labels.py - Extract components, labels, fix-versions, and linked
test cases from pasted Jira ticket text.

Usage:
    python extract-jira-labels.py <ticket-file>
    python extract-jira-labels.py --stdin  (read ticket text from stdin)

Output: JSON to stdout with extracted fields.
"""

import sys
import re
import json
import argparse
from pathlib import Path


def extract_ticket_fields(text: str) -> dict:
    """Extract structured fields from Jira ticket text."""
    result = {
        "ticket_id": None,
        "summary": None,
        "description": None,
        "components": [],
        "labels": [],
        "fix_versions": [],
        "priority": None,
        "issue_type": None,
        "linked_issues": [],
        "linked_test_cases": [],
        "high_signal_labels": [],
        "change_type": None,
    }

    lines = text.strip().splitlines()
    current_field = None
    description_lines = []

    # Patterns for field extraction
    ticket_id_pattern = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
    field_patterns = {
        "summary": re.compile(r"^(?:Summary|Title)\s*[:=]\s*(.+)", re.IGNORECASE),
        "components": re.compile(r"^(?:Component|Components|Component/s)\s*[:=]\s*(.+)", re.IGNORECASE),
        "labels": re.compile(r"^(?:Label|Labels)\s*[:=]\s*(.+)", re.IGNORECASE),
        "fix_versions": re.compile(r"^(?:Fix Version|Fix Versions|Fix Version/s)\s*[:=]\s*(.+)", re.IGNORECASE),
        "priority": re.compile(r"^(?:Priority)\s*[:=]\s*(.+)", re.IGNORECASE),
        "issue_type": re.compile(r"^(?:Issue Type|Type)\s*[:=]\s*(.+)", re.IGNORECASE),
    }

    # High-signal labels that affect risk classification
    high_signal_set = {
        "breaking-change", "security", "migration", "high-risk", "hotfix",
        "performance", "data-integrity", "compliance", "pii", "auth",
        "breaking", "critical", "production-fix", "rollback",
    }

    for line in lines:
        stripped = line.strip()

        # Extract ticket IDs anywhere in the text
        for match in ticket_id_pattern.finditer(stripped):
            tid = match.group(1)
            if result["ticket_id"] is None:
                result["ticket_id"] = tid
            # Check if it looks like a test case reference
            if any(prefix in tid.upper() for prefix in ["TC-", "TEST-", "QA-"]):
                if tid not in result["linked_test_cases"]:
                    result["linked_test_cases"].append(tid)
            elif tid != result["ticket_id"] and tid not in result["linked_issues"]:
                result["linked_issues"].append(tid)

        # Check for known field patterns
        matched = False
        for field_name, pattern in field_patterns.items():
            m = pattern.match(stripped)
            if m:
                value = m.group(1).strip()
                if field_name in ("components", "labels", "fix_versions"):
                    items = [v.strip() for v in re.split(r"[,;]", value) if v.strip()]
                    result[field_name] = items
                else:
                    result[field_name] = value
                current_field = field_name
                matched = True
                break

        # Check for Description field start
        if re.match(r"^(?:Description)\s*[:=]?\s*(.*)", stripped, re.IGNORECASE):
            desc_match = re.match(r"^(?:Description)\s*[:=]?\s*(.*)", stripped, re.IGNORECASE)
            remainder = desc_match.group(1).strip() if desc_match else ""
            if remainder:
                description_lines.append(remainder)
            current_field = "description"
            matched = True

        # Linked issues patterns
        linked_match = re.match(
            r"^(?:Linked Issues?|Links?|Related|Blocks|Blocked by|is blocked by|relates to)\s*[:=]?\s*(.+)",
            stripped, re.IGNORECASE,
        )
        if linked_match:
            for tid in ticket_id_pattern.findall(linked_match.group(1)):
                if tid not in result["linked_issues"]:
                    result["linked_issues"].append(tid)
            matched = True

        # If we are in the description field and the line is not a new field, accumulate
        if not matched and current_field == "description":
            description_lines.append(stripped)

    # Finalize description
    if description_lines:
        result["description"] = "\n".join(description_lines).strip()

    # Identify high-signal labels
    for label in result["labels"]:
        if label.lower().replace("_", "-") in high_signal_set:
            result["high_signal_labels"].append(label)

    # Classify change type from summary and labels
    result["change_type"] = _classify_change_type(
        result.get("summary", "") or "",
        result.get("description", "") or "",
        result.get("labels", []),
        result.get("issue_type", "") or "",
    )

    return result


def _classify_change_type(summary: str, description: str, labels: list, issue_type: str) -> str:
    """Classify the type of change based on available signals."""
    combined = f"{summary} {description} {issue_type} {' '.join(labels)}".lower()

    if any(kw in combined for kw in ["bug", "fix", "defect", "hotfix", "patch"]):
        return "bug_fix"
    if any(kw in combined for kw in ["migrat", "schema", "alembic", "flyway"]):
        return "data_migration"
    if any(kw in combined for kw in ["refactor", "cleanup", "tech debt", "reorganiz"]):
        return "refactor"
    if any(kw in combined for kw in ["config", "environment", "feature flag", "toggle"]):
        return "config_change"
    if any(kw in combined for kw in ["new feature", "add", "implement", "introduce", "enhancement"]):
        return "new_feature"
    if any(kw in combined for kw in ["deprecat", "remove", "sunset", "disable"]):
        return "deprecation"
    if any(kw in combined for kw in ["performance", "optimization", "speed", "latency"]):
        return "performance"
    return "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured fields from pasted Jira ticket text"
    )
    parser.add_argument("ticket_file", nargs="?", help="Path to ticket text file")
    parser.add_argument("--stdin", action="store_true", help="Read ticket text from stdin")
    args = parser.parse_args()

    if args.stdin:
        text = sys.stdin.read()
    elif args.ticket_file:
        path = Path(args.ticket_file)
        if not path.exists():
            print(f"Error: File not found: {args.ticket_file}", file=sys.stderr)
            sys.exit(1)
        text = path.read_text(encoding="utf-8")
    else:
        parser.print_help()
        sys.exit(1)

    result = extract_ticket_fields(text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
