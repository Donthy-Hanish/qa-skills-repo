#!/usr/bin/env python3
"""
render-report.py - Render a completed change-impact analysis into both
Markdown and JSON report files.

Usage:
    python render-report.py <analysis-json> [--output-dir <dir>]

Input: A JSON file containing the structured analysis data.
Output: Two files in the output directory:
    - impact-report.md  (Markdown)
    - impact-report.json (JSON)

The input JSON should follow the schema defined in
references/report-templates/impact-report.json.
"""

import sys
import json
import argparse
import textwrap
from datetime import datetime
from pathlib import Path


def render_markdown(data: dict) -> str:
    """Render the analysis data as a Markdown report."""
    lines = []

    # Header
    lines.append("# Change Impact Report")
    lines.append("")

    # Change Summary
    cs = data.get("change_summary", {})
    lines.append("## Change Summary")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| Change ID | {cs.get('change_id', 'N/A')} |")
    lines.append(f"| Change Title | {cs.get('title', 'N/A')} |")
    lines.append(f"| Input Type | {cs.get('input_type', 'N/A')} |")
    lines.append(f"| Analysis Date | {cs.get('analysis_date', datetime.now().strftime('%Y-%m-%d'))} |")
    lines.append(f"| Analyst | {cs.get('analyst', 'N/A')} |")
    lines.append("")

    # Change Description
    lines.append("## Change Description")
    lines.append("")
    lines.append(data.get("change_description", "No description provided."))
    lines.append("")

    # Affected Areas
    areas = data.get("affected_areas", [])
    lines.append("## Affected Areas")
    lines.append("")
    if areas:
        lines.append("| # | Area / Module | Impact Type | Risk Level | Risk Rationale |")
        lines.append("|---|---------------|-------------|------------|----------------|")
        for area in areas:
            esc_flag = ""
            if area.get("escalation_applied"):
                esc_flag = f" (escalated: {area.get('escalation_reason', '')})"
            lines.append(
                f"| {area.get('id', '')} "
                f"| {area.get('area', '')} "
                f"| {area.get('impact_type', '')} "
                f"| {area.get('risk_level', '').upper()}{esc_flag} "
                f"| {area.get('risk_rationale', '')} |"
            )
        lines.append("")
    else:
        lines.append("No affected areas identified.")
        lines.append("")

    # Tests to Run
    tests = data.get("tests_to_run", {})
    lines.append("## Tests to Run")
    lines.append("")

    if not tests.get("test_map_loaded", False):
        note = tests.get("note", "No project test map loaded.")
        lines.append(f"> **Note:** {note}")
        lines.append("")

    by_risk = tests.get("by_risk_level", {})
    for level in ["critical", "high", "medium", "low"]:
        items = by_risk.get(level, [])
        if items:
            lines.append(f"### {level.capitalize()} Risk Areas")
            lines.append("")
            for item in items:
                if isinstance(item, dict):
                    lines.append(f"- **{item.get('area', '')}**: {item.get('tests', 'No mapped tests')}")
                else:
                    lines.append(f"- {item}")
            lines.append("")

    # Automated suites
    auto = tests.get("automated_suites", [])
    if auto:
        lines.append("### Automated Suites")
        lines.append("")
        lines.append("| Suite / Tag | Estimated Run Time | Covers |")
        lines.append("|-------------|-------------------|--------|")
        for s in auto:
            lines.append(
                f"| {s.get('suite_or_tag', '')} "
                f"| {s.get('estimated_run_time', '')} "
                f"| {s.get('covers', '')} |"
            )
        lines.append("")

    # Manual tests
    manual = tests.get("manual_tests", [])
    if manual:
        lines.append("### Manual Tests")
        lines.append("")
        lines.append("| Test ID | Test Name | Module | Priority |")
        lines.append("|---------|-----------|--------|----------|")
        for t in manual:
            lines.append(
                f"| {t.get('test_id', '')} "
                f"| {t.get('test_name', '')} "
                f"| {t.get('module', '')} "
                f"| {t.get('priority', '')} |"
            )
        lines.append("")

    # Regression Scope
    scope = data.get("regression_scope", {})
    lines.append("## Regression Scope Recommendation")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| Recommended Scope | {scope.get('recommended', 'N/A')} |")
    lines.append(f"| Rationale | {scope.get('rationale', 'N/A')} |")
    lines.append(f"| Estimated Effort | {scope.get('estimated_effort', 'N/A')} |")
    lines.append("")

    # Coverage Gaps
    gaps = data.get("coverage_gaps", [])
    lines.append("## Coverage Gaps")
    lines.append("")
    if gaps:
        lines.append("| # | Area | Why Affected | Risk Introduced | Suggested Test Type |")
        lines.append("|---|------|-------------|-----------------|---------------------|")
        for g in gaps:
            lines.append(
                f"| {g.get('id', '')} "
                f"| {g.get('area', '')} "
                f"| {g.get('why_affected', '')} "
                f"| {g.get('risk_introduced', '')} "
                f"| {g.get('suggested_test_type', '')} |"
            )
        lines.append("")
    else:
        lines.append("No coverage gaps identified.")
        lines.append("")

    # Notes
    notes = data.get("notes", [])
    if notes:
        lines.append("## Notes and Caveats")
        lines.append("")
        for note in notes:
            lines.append(f"- {note}")
        lines.append("")

    return "\n".join(lines)


def render_json(data: dict) -> str:
    """Render the analysis data as a formatted JSON report."""
    # Ensure schema version
    data.setdefault("_schema_version", "1.0.0")
    # Ensure analysis date
    if "change_summary" in data:
        data["change_summary"].setdefault(
            "analysis_date", datetime.now().strftime("%Y-%m-%d")
        )
    return json.dumps(data, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Render change-impact analysis into Markdown and JSON reports"
    )
    parser.add_argument("analysis_json", help="Path to the analysis data JSON file")
    parser.add_argument(
        "--output-dir", default=".", help="Directory to write reports to (default: current directory)"
    )
    args = parser.parse_args()

    # Read input
    input_path = Path(args.analysis_json)
    if not input_path.exists():
        print(f"Error: File not found: {args.analysis_json}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))

    # Render
    md_content = render_markdown(data)
    json_content = render_json(data)

    # Write outputs
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / "impact-report.md"
    json_path = output_dir / "impact-report.json"

    md_path.write_text(md_content, encoding="utf-8")
    json_path.write_text(json_content, encoding="utf-8")

    print(f"Markdown report: {md_path}")
    print(f"JSON report:     {json_path}")


if __name__ == "__main__":
    main()
