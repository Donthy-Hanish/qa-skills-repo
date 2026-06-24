import os
import re
import sys
import argparse
import xml.etree.ElementTree as ET

class FlakyTestAnalyzer:
    def __init__(self):
        self.flaky_tests = {}
        self.compliance_score = 100
        self.violations = []

    def parse_robot_run(self, file_path):
        """
        Parses output.xml and returns a dictionary of {test_name: (status, error_message)}
        """
        if not os.path.exists(file_path):
            print(f"Error: Run file '{file_path}' does not exist.")
            return {}

        results = {}
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find all test elements
            for test in root.iter('test'):
                test_name = test.get('name')
                status_elem = test.find('status')
                status = status_elem.get('status') if status_elem is not None else "UNKNOWN"
                
                # Get message/error traceback if failed
                error_msg = ""
                if status == "FAIL" and status_elem is not None:
                    error_msg = status_elem.text or ""
                    
                results[test_name] = (status, error_msg)
        except Exception as e:
            print(f"Error parsing Robot XML file '{file_path}': {e}")
        return results

    def compare_runs(self, run_files):
        """
        Compares statuses across multiple run outputs.
        """
        all_runs = []
        for rf in run_files:
            run_data = self.parse_robot_run(rf)
            if run_data:
                all_runs.append((rf, run_data))

        if len(all_runs) < 2:
            print("Error: Need at least 2 valid XML runs to compare for flakiness.")
            return {}

        flaky_results = {}
        # Get all distinct test names
        all_test_names = set()
        for _, r_data in all_runs:
            all_test_names.update(r_data.keys())

        for name in all_test_names:
            statuses = []
            errors = []
            for rf, r_data in all_runs:
                if name in r_data:
                    stat, err = r_data[name]
                    statuses.append(stat)
                    errors.append(err)
                else:
                    statuses.append("MISSING")
                    errors.append("")

            # A test is flaky if its status changes across runs (excluding MISSING)
            active_statuses = [s for s in statuses if s != "MISSING"]
            if len(set(active_statuses)) > 1:
                # Find the primary failure error message
                primary_err = next((err for err in errors if err), "Unknown failure")
                category = self.categorize_error(primary_err)
                flaky_results[name] = {
                    "statuses": statuses,
                    "primary_error": primary_err,
                    "category": category
                }
        
        self.flaky_tests = flaky_results
        return flaky_results

    def categorize_error(self, error_msg):
        """
        Performs RCA categorization based on error message substrings.
        """
        err_lower = error_msg.lower()
        
        # Timing exceptions
        if any(term in err_lower for term in ["timeout", "timed out", "interactable", "not visible", "loading"]):
            return "Timing Flake"
        # Stale element reference
        elif "stale" in err_lower:
            return "Timing Flake"
        # Network or API issues
        elif any(term in err_lower for term in ["connectionrefused", "http 5", "502", "503", "gateway", "connection error"]):
            return "Network/API Flake"
        # Locator issues
        elif any(term in err_lower for term in ["nosuchelement", "elementnotfound", "xpathlookup", "unable to locate"]):
            return "Locator Flake"
        # Data dependency
        elif any(term in err_lower for term in ["duplicate", "unique constraint", "already exists", "value mismatch", "expected", "but got"]):
            return "Data Flake"
            
        return "Unclassified/Functional Failure"

    def audit_directory_locators(self, dir_path):
        """
        Scans robot/resource files for Test Locator Standard violations.
        """
        if not os.path.exists(dir_path):
            print(f"Error: Audit directory '{dir_path}' does not exist.")
            return

        violations = []
        # Traverses files
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith((".robot", ".resource")):
                    file_path = os.path.join(root, file)
                    file_violations = self.audit_file(file_path)
                    violations.extend(file_violations)
                    
        self.violations = violations
        
        # Calculate Compliance Score: deduct 10 points for each Critical, 3 for Suggestion, min 0
        score = 100
        for v in violations:
            if v["severity"] == "CRITICAL":
                score -= 10
            else:
                score -= 3
        self.compliance_score = max(0, score)
        return violations

    def audit_file(self, file_path):
        violations = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for idx, line in enumerate(lines):
            line_num = idx + 1
            line_str = line.strip()
            
            # Match elements of locator keywords: Click Element, Input Text, Wait Until Element..., etc.
            # Example: Click Element    xpath=//div[3]/span/button
            match = re.search(r'(?:Click Element|Input Text|Wait Until Element|Element Should Be)\s+(.*)', line)
            if match:
                locator_arg = match.group(1).strip()
                # Split locator arg from variables/values if dynamic
                loc_parts = re.split(r'\s{2,}', locator_arg)
                locator = loc_parts[0]
                
                # Check 1: Absolute XPath
                if "xpath=" in locator.lower() or locator.startswith("//"):
                    # Check for deep structural xpath without stable anchors
                    if re.search(r'/(?:div|span|p|tr|td|li)/', locator) and not "@" in locator:
                        violations.append({
                            "file": os.path.basename(file_path),
                            "line": line_num,
                            "locator": locator,
                            "type": "Absolute/Index-based XPath",
                            "severity": "CRITICAL",
                            "detail": "Absolute XPath overrides the locator contract and easily breaks on React/Kendo DOM updates.",
                            "recommendation": "Use css=[data-testid='...'] or aria-label instead."
                        })
                    # Check 2: Index-based XPath
                    elif re.search(r'\[\d+\]', locator):
                        violations.append({
                            "file": os.path.basename(file_path),
                            "line": line_num,
                            "locator": locator,
                            "type": "Index-based selector",
                            "severity": "MEDIUM",
                            "detail": "Index selectors are fragile. A new list item or structural change will break the index.",
                            "recommendation": "Add a descriptive data-testid to the list element."
                        })
                
                # Check 3: Dynamic ID selectors
                id_match = re.search(r'(?:id=|#)(k-[a-fA-F0-9\-]{5,}|kendo-\d+|\d{5,})', locator, re.IGNORECASE)
                if id_match:
                    violations.append({
                        "file": os.path.basename(file_path),
                        "line": line_num,
                        "locator": locator,
                        "type": "Dynamic Framework ID",
                        "severity": "CRITICAL",
                        "detail": f"Detected auto-generated framework ID: '{id_match.group(1)}'. These change on every page load.",
                        "recommendation": "Request a stable custom attribute like data-testid from development."
                    })
                    
                # Check 4: Dynamic class/css index
                if "css=" in locator.lower() and ":nth-child" in locator.lower():
                    violations.append({
                        "file": os.path.basename(file_path),
                        "line": line_num,
                        "locator": locator,
                        "type": "Fragile CSS Selector",
                        "severity": "MEDIUM",
                        "detail": "Uses dynamic css structural pseudo-class (:nth-child).",
                        "recommendation": "Use stable visible text or data-testid instead."
                    })

                # Check 5: Non-standard naming convention
                testid_naming = re.search(r'data-testid=["\']([^"\']+)["\']', locator)
                if testid_naming:
                    val = testid_naming.group(1)
                    if "_" in val or re.search(r'[A-Z]', val):
                        violations.append({
                            "file": os.path.basename(file_path),
                            "line": line_num,
                            "locator": locator,
                            "type": "Locator Naming Mismatch",
                            "severity": "LOW",
                            "detail": f"Test Locator Standard naming rule violation in '{val}'. Name must be in lowercase kebab-case.",
                            "recommendation": "Rename attribute to lowercase-kebab-case (e.g. submit-order instead of submit_order)."
                        })

        return violations

    def generate_report(self, run_files, audit_dir, output_path):
        """
        Assembles comparison results and locator compliance violations into markdown format.
        """
        flaky_count = len(self.flaky_tests)
        total_tests = 0
        
        # Calculate totals from runs
        if run_files:
            run_data = self.parse_robot_run(run_files[0])
            total_tests = len(run_data)

        report_md = []
        report_md.append("# Flaky Test & Compliance Analysis Report\n")
        
        # Section 1: Executive Summary
        report_md.append("## 1. Executive Summary")
        if run_files:
            report_md.append(f"- **Total Tests Analyzed**: {total_tests}")
            report_md.append(f"- **Flaky Tests Detected**: {flaky_count} ({round((flaky_count/max(1, total_tests))*100, 1)}%)")
        else:
            report_md.append("- **Run Flakiness Analysis**: Not run (No output.xml provided)")
            
        if audit_dir:
            report_md.append(f"- **Compliance Score**: {self.compliance_score}/100")
            report_md.append(f"- **Total Standard Violations**: {len(self.violations)}")
        else:
            report_md.append("- **Locator Standard Audit**: Not run (No files audited)")
            
        # Deduce primary flakiness driver
        if self.flaky_tests:
            cats = [test_info["category"] for test_info in self.flaky_tests.values()]
            if cats:
                primary = max(set(cats), key=cats.count)
                report_md.append(f"- **Primary Flakiness Driver**: {primary}")
        report_md.append("\n")

        # Section 2: Flaky Test Details
        if run_files and self.flaky_tests:
            report_md.append("## 2. Flaky Test Summary")
            report_md.append("| Test Case Name | Run Statuses | Root Cause Category | Primary Exception Details |")
            report_md.append("| :--- | :--- | :--- | :--- |")
            for t_name, data in self.flaky_tests.items():
                statuses_str = " -> ".join(data["statuses"])
                report_md.append(f"| `{t_name}` | {statuses_str} | **{data['category']}** | `{data['primary_error'][:100]}` |")
            report_md.append("\n")

            report_md.append("## 3. Root Cause Analysis (RCA) Details")
            for t_name, data in self.flaky_tests.items():
                report_md.append(f"### {t_name}")
                report_md.append(f"- **Category**: {data['category']}")
                report_md.append("- **Symptom Exception Traceback**:")
                report_md.append("  ```")
                report_md.append(f"  {data['primary_error']}")
                report_md.append("  ```")
                report_md.append("- **Recommended Actionable Remediation**:")
                if data["category"] == "Timing Flake":
                    report_md.append("  - Replace hardcoded Sleep keywords with dynamic waiting (e.g. Smart Wait For Element).")
                    report_md.append("  - Increase default timeout if background React rendering is slow on CI/CD.")
                elif data["category"] == "Locator Flake":
                    report_md.append("  - Element path changed. Transition locator to data-testid or aria-label.")
                    report_md.append("  - Utilize SelfHealingLibrary at runtime to auto-discover locator variants.")
                elif data["category"] == "Data Flake":
                    report_md.append("  - Ensure fresh test databases or append unique random strings/timestamps to test payloads.")
                    report_md.append("  - Implement clean Tear Down keywords to release resources.")
                elif data["category"] == "Network/API Flake":
                    report_md.append("  - Review gateway routing or enable API endpoint retry policies in Robot setup.")
                else:
                    report_md.append("  - Investigate application code logic. Assertions might be overly rigid.")
                report_md.append("\n")

        # Section 3: Compliance Audit Details
        if audit_dir and self.violations:
            report_md.append("## 4. Test Locator Compliance Audit")
            report_md.append("The following locators violate the team's [Test Locator Standard](file:///C:/Users/costrategix/.gemini/antigravity-ide/brain/SkillCreatorPOC/Reference/Test%20Locator%20Standard.pdf):")
            report_md.append("")
            
            criticals = [v for v in self.violations if v["severity"] == "CRITICAL"]
            mediums = [v for v in self.violations if v["severity"] == "MEDIUM"]
            lows = [v for v in self.violations if v["severity"] == "LOW"]
            
            if criticals:
                report_md.append("### Critical Violations (0% Tolerance)")
                for v in criticals:
                    report_md.append(f"- **{v['file']}:L{v['line']}** - `{v['locator']}`")
                    report_md.append(f"  - *Type*: {v['type']}")
                    report_md.append(f"  - *Detail*: {v['detail']}")
                    report_md.append(f"  - *Remedy*: {v['recommendation']}")
                report_md.append("")
                
            if mediums:
                report_md.append("### Medium/Fragile Violations")
                for v in mediums:
                    report_md.append(f"- **{v['file']}:L{v['line']}** - `{v['locator']}`")
                    report_md.append(f"  - *Type*: {v['type']}")
                    report_md.append(f"  - *Detail*: {v['detail']}")
                    report_md.append(f"  - *Remedy*: {v['recommendation']}")
                report_md.append("")
                
            if lows:
                report_md.append("### Minor Naming Compliance")
                for v in lows:
                    report_md.append(f"- **{v['file']}:L{v['line']}** - `{v['locator']}`")
                    report_md.append(f"  - *Type*: {v['type']}")
                    report_md.append(f"  - *Detail*: {v['detail']}")
                    report_md.append(f"  - *Remedy*: {v['recommendation']}")
                report_md.append("")
        elif audit_dir:
            report_md.append("## 4. Test Locator Compliance Audit")
            report_md.append("🎉 All tested locators fully comply with the Test Locator Standard!")

        report_md.append("\n---\n*Report generated by Flaky Test & Self-Healing Analyzer*")

        final_report = "\n".join(report_md)
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(final_report)
        print(f"Success: Analysis report written to '{output_path}'")

def run_self_test():
    print("FlakyTestAnalyzer: Starting offline self-test...")
    analyzer = FlakyTestAnalyzer()
    
    # 1. Create Mock Robot Output files
    mock_xml1 = """<?xml version="1.0" encoding="UTF-8"?>
    <robot>
      <suite name="Checkout Suite">
        <test name="Buy Product">
          <status status="FAIL">TimeoutException: Element css=[data-testid="pay-btn"] not visible after 5s</status>
        </test>
        <test name="Login User">
          <status status="PASS"></status>
        </test>
      </suite>
    </robot>
    """
    
    mock_xml2 = """<?xml version="1.0" encoding="UTF-8"?>
    <robot>
      <suite name="Checkout Suite">
        <test name="Buy Product">
          <status status="PASS"></status>
        </test>
        <test name="Login User">
          <status status="PASS"></status>
        </test>
      </suite>
    </robot>
    """
    
    with open("temp_run1.xml", "w", encoding="utf-8") as f:
        f.write(mock_xml1)
    with open("temp_run2.xml", "w", encoding="utf-8") as f:
        f.write(mock_xml2)
        
    # Test compare runs
    flaky = analyzer.compare_runs(["temp_run1.xml", "temp_run2.xml"])
    print(f"Detected flaky tests: {list(flaky.keys())}")
    assert "Buy Product" in flaky
    assert flaky["Buy Product"]["category"] == "Timing Flake"
    
    # 2. Create Mock Robot script for auditing
    mock_robot = """*** Test Cases ***
    Checkout Item
        Click Element    xpath=//div[3]/span/button
        Input Text       id=k-98312-email    test@email.com
        Click Element    css=[data-testid="Submit_Order"]
        Wait Until Element    css=div:nth-child(3)
    """
    with open("temp_test.robot", "w", encoding="utf-8") as f:
        f.write(mock_robot)
        
    # Audit file
    viols = analyzer.audit_file("temp_test.robot")
    print(f"Found {len(viols)} violations in temp_test.robot")
    assert len(viols) == 4
    
    # Generate Report
    analyzer.audit_directory_locators(".")
    analyzer.generate_report(["temp_run1.xml", "temp_run2.xml"], ".", "temp_report.md")
    
    # Clean up temp files
    os.remove("temp_run1.xml")
    os.remove("temp_run2.xml")
    os.remove("temp_test.robot")
    os.remove("temp_report.md")
    
    print("Offline Self-Test: PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_self_test()
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Audits Robot test files against Locator Standards and detects flakiness from run outputs.")
    parser.add_argument("--runs", nargs="+", help="Path to two or more output.xml files to compare for flakiness.")
    parser.add_argument("--audit", help="Directory containing .robot/.resource files to audit for Locator Standard compliance.")
    parser.add_argument("--output", default="./flakiness_analysis_report.md", help="Output path for the generated markdown report.")
    
    args = parser.parse_args()
    
    if not args.runs and not args.audit:
        parser.print_help()
        sys.exit(1)
        
    analyzer = FlakyTestAnalyzer()
    if args.runs:
        analyzer.compare_runs(args.runs)
    if args.audit:
        analyzer.audit_directory_locators(args.audit)
        
    analyzer.generate_report(args.runs, args.audit, args.output)
