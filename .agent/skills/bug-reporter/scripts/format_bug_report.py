import os
import re
import sys
import argparse

class BugReportFormatter:
    def __init__(self):
        self.mandatory_headers = {
            "summary": [r'#', r'Executive Summary', r'Summary'],
            "environment": [r'Environment Details', r'Environment'],
            "steps": [r'Steps to Reproduce', r'Steps'],
            "expected_vs_actual": [r'Expected vs Actual Behavior', r'Expected vs Actual', r'Expected', r'Actual'],
            "evidence": [r'Technical Evidence', r'Diagnostics', r'Evidence', r'Stacktrace', r'Payload'],
            "impact": [r'Business Impact', r'Impact', r'Scope Risk', r'Risk']
        }

    def validate_report(self, file_path):
        """
        Parses a bug report markdown file and calculates a completeness and quality score.
        """
        if not os.path.exists(file_path):
            print(f"Error: Report file '{file_path}' does not exist.")
            return None

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        score = 0
        score_breakdown = {}
        suggestions = []
        
        # 1. Verify Defect Class and Executive Summary (Triage details)
        triage_found = False
        for head in ["Executive Summary", "Summary", "triage", "Summary"]:
            if re.search(rf'##?.*{head}', content, re.IGNORECASE):
                triage_found = True
                break
        
        has_sev = re.search(r'Severity\s*:\s*\S+', content, re.IGNORECASE)
        has_prio = re.search(r'Priority\s*:\s*\S+', content, re.IGNORECASE)
        
        if triage_found and has_sev and has_prio:
            score += 20
            score_breakdown["Summary & Triage (20 pts)"] = 20
        else:
            deduct = 0
            if triage_found: deduct += 10
            if has_sev: deduct += 5
            if has_prio: deduct += 5
            score += deduct
            score_breakdown["Summary & Triage (20 pts)"] = deduct
            suggestions.append("Missing explicit 'Severity' or 'Priority' classification under Executive Summary.")

        # 2. Verify Environment Details
        env_found = False
        for head in self.mandatory_headers["environment"]:
            if re.search(rf'##?.*{head}', content, re.IGNORECASE):
                env_found = True
                break
        if env_found:
            score += 20
            score_breakdown["Environment Details (20 pts)"] = 20
        else:
            score_breakdown["Environment Details (20 pts)"] = 0
            suggestions.append("Missing 'Environment Details' section (OS, browser, build details, or environment).")

        # 3. Verify Steps to Reproduce
        steps_found = False
        for head in self.mandatory_headers["steps"]:
            if re.search(rf'##?.*{head}', content, re.IGNORECASE):
                steps_found = True
                break
        
        # Check for numbered list under steps
        has_list = re.search(r'\d+\.\s+\S+', content)
        if steps_found and has_list:
            score += 20
            score_breakdown["Steps to Reproduce (20 pts)"] = 20
        elif steps_found:
            score += 10
            score_breakdown["Steps to Reproduce (20 pts)"] = 10
            suggestions.append("Steps section exists but is not formatted as a numbered list (1., 2., 3.).")
        else:
            score_breakdown["Steps to Reproduce (20 pts)"] = 0
            suggestions.append("Missing 'Steps to Reproduce' section.")

        # 4. Verify Expected vs Actual
        exp_found = False
        for head in self.mandatory_headers["expected_vs_actual"]:
            if re.search(rf'##?.*{head}', content, re.IGNORECASE):
                exp_found = True
                break
        has_expected = re.search(r'Expected\s+Behavior|Expected', content, re.IGNORECASE)
        has_actual = re.search(r'Actual\s+Behavior|Actual', content, re.IGNORECASE)
        
        if exp_found and has_expected and has_actual:
            score += 20
            score_breakdown["Expected vs Actual (20 pts)"] = 20
        else:
            deduct = 0
            if exp_found: deduct += 10
            if has_expected: deduct += 5
            if has_actual: deduct += 5
            score += deduct
            score_breakdown["Expected vs Actual (20 pts)"] = deduct
            suggestions.append("Missing explicit 'Expected Behavior' or 'Actual Behavior' comparisons.")

        # 5. Verify Technical Evidence (Logs, traces, code blocks)
        evidence_found = False
        for head in self.mandatory_headers["evidence"]:
            if re.search(rf'##?.*{head}', content, re.IGNORECASE):
                evidence_found = True
                break
        has_code_block = "```" in content
        
        if evidence_found and has_code_block:
            score += 20
            score_breakdown["Technical Evidence (20 pts)"] = 20
        elif evidence_found:
            score += 10
            score_breakdown["Technical Evidence (20 pts)"] = 10
            suggestions.append("Evidence section exists but lacks code blocks (```) enclosing logs or payloads.")
        else:
            score_breakdown["Technical Evidence (20 pts)"] = 0
            suggestions.append("Missing 'Technical Evidence' section to supply stack traces or API details.")

        # 6. Extra Quality Check: Business Impact
        impact_found = False
        for head in self.mandatory_headers["impact"]:
            if re.search(rf'##?.*{head}', content, re.IGNORECASE):
                impact_found = True
                break
        if not impact_found:
            suggestions.append("Tip: Add a 'Business Impact' section to describe financial, legal, or UX risks.")

        return {
            "score": score,
            "breakdown": score_breakdown,
            "suggestions": suggestions
        }

    def format_report(self, title, bug_class, severity, priority, steps, expected, actual, env, evidence, impact=None):
        """
        Assembles report variables into standard compliance markdown format.
        """
        formatted_steps = ""
        for i, step in enumerate(steps.split(";")):
            if step.strip():
                formatted_steps += f"{i+1}. {step.strip()}\n"

        report = []
        report.append(f"# [BUG] {title}\n")
        report.append("## 1. Executive Summary")
        report.append(f"- **Defect Class**: {bug_class}")
        report.append(f"- **Severity**: {severity}")
        report.append(f"- **Priority**: {priority}")
        if impact:
            report.append(f"- **Business Impact**: {impact}")
        report.append("\n## 2. Environment Details")
        report.append(f"- **Environment**: {env}")
        
        report.append("\n## 3. Steps to Reproduce")
        report.append(formatted_steps)
        
        report.append("## 4. Expected vs Actual Behavior")
        report.append(f"- **Expected Behavior**: {expected}")
        report.append(f"- **Actual Behavior**: {actual}")
        
        report.append("\n## 5. Technical Evidence & Diagnostics")
        report.append("### Diagnostic Logs")
        report.append("```")
        report.append(evidence)
        report.append("```")
        
        if impact:
            report.append("\n## 6. Business Impact & Scope Risk")
            report.append(f"- **Impact Detail**: {impact}")
            
        report.append("\n---\n*Defect report compiled by Enterprise Bug Reporter Agent*")
        return "\n".join(report)

def run_self_test():
    print("BugReportFormatter: Starting offline self-test...")
    formatter = BugReportFormatter()
    
    # Generate mock bug report
    mock_report = """# [BUG] Mobile Checkout visual layout shift

## 1. Executive Summary
- Defect Class: UI Functional Bug
- Severity: S2 Major
- Priority: P2 High

## 2. Environment Details
- Environment: Staging
- Browser: Chrome Mobile
- OS: iOS 17.2

## 3. Steps to Reproduce
1. Log into the platform.
2. Go to the checkout basket.
3. Click the Apply Discount button.

## 4. Expected vs Actual Behavior
- Expected Behavior: Discount code is verified and card summary remains inside viewport.
- Actual Behavior: Discount code is verified, but card summary shifts visually below the footer.

## 5. Technical Evidence & Diagnostics
### Chrome console
```
Uncaught ReferenceError: handleLayoutShift is not defined at checkout.js:142
```

## 6. Business Impact
- User cannot complete payment due to shifted layout elements.
"""
    
    with open("temp_bug.md", "w", encoding="utf-8") as f:
        f.write(mock_report)
        
    res = formatter.validate_report("temp_bug.md")
    print(f"Validated mock report. Total Score: {res['score']}/100")
    print(f"Suggestions: {res['suggestions']}")
    
    assert res['score'] == 100
    os.remove("temp_bug.md")
    
    # Test format function
    report_text = formatter.format_report(
        title="Payment API Timeout",
        bug_class="API Bug",
        severity="S1 Blocker",
        priority="P1 Immediate",
        steps="Navigate to payment screen; Click Submit; Observe loader spinner time out",
        expected="API returns 200 OK within 2 seconds",
        actual="API request times out after 30 seconds with 504 Gateway Timeout",
        env="Staging Gateway",
        evidence="HTTP/1.1 504 Gateway Timeout\nConnection: keep-alive",
        impact="Blocks all checkout attempts on Staging"
    )
    print("Formatting test output length check: PASSED" if len(report_text) > 100 else "Formatting test: FAILED")
    print("Offline Self-Test: PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_self_test()
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Audits and formats enterprise-grade bug reports.")
    parser.add_argument("--validate", help="Path to a markdown bug report file to validate.")
    parser.add_argument("--format", action="store_true", help="Auto-generates a structured report based on parameters.")
    parser.add_argument("--title", help="Title of the bug report.")
    parser.add_argument("--bug-class", choices=["UI Functional Bug", "API Bug", "AI/LLM Bug"], help="Category of defect.")
    parser.add_argument("--severity", help="Severity rating (e.g. S1 Blocker, S2 Major).")
    parser.add_argument("--priority", help="Priority rating (e.g. P1 Immediate, P2 High).")
    parser.add_argument("--steps", help="Semicolon-separated list of steps to reproduce.")
    parser.add_argument("--expected", help="Description of expected behavior.")
    parser.add_argument("--actual", help="Description of actual behavior.")
    parser.add_argument("--env", help="Environment information.")
    parser.add_argument("--evidence", help="Raw terminal logs or stack trace.")
    parser.add_argument("--impact", help="Description of business/operational impact.")
    parser.add_argument("--output", default="./formatted_bug_report.md", help="Destination file path for generated report.")

    args = parser.parse_args()

    if not args.validate and not args.format:
        parser.print_help()
        sys.exit(1)

    formatter = BugReportFormatter()
    
    if args.validate:
        res = formatter.validate_report(args.validate)
        if res:
            print("\n==========================================")
            print("         BUG REPORT COMPLETENESS SCORECARD")
            print("==========================================")
            print(f"Overall Quality Score: {res['score']}/100")
            print("\nScore Breakdown:")
            for area, pt in res['breakdown'].items():
                print(f" - {area}: {pt} pts")
            if res['suggestions']:
                print("\nRecommended Remediation Actions:")
                for sugg in res['suggestions']:
                    print(f" [!] {sugg}")
            else:
                print("\n🎉 Exceptional! The bug report contains all required mandatory sections and quality evidence!")
            print("==========================================\n")
            
    elif args.format:
        if not (args.title and args.bug_class and args.severity and args.priority and args.steps and args.expected and args.actual and args.env and args.evidence):
            print("Error: Formatting requires all core arguments. Run with --help to see mandatory options.")
            sys.exit(1)
            
        report_out = formatter.format_report(
            title=args.title,
            bug_class=args.bug_class,
            severity=args.severity,
            priority=args.priority,
            steps=args.steps,
            expected=args.expected,
            actual=args.actual,
            env=args.env,
            evidence=args.evidence,
            impact=args.impact
        )
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report_out)
        print(f"Success: Standard-compliant bug report written to '{args.output}'")
