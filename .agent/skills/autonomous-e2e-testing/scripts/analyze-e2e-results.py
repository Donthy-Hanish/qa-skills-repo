import sys
import xml.etree.ElementTree as ET
import json
import os

def analyze_pytest_json(filepath):
    """
    Parses pytest json-report format to extract E2E stats and slow execution times.
    """
    if not os.path.exists(filepath):
        print(f"Error: pytest result file {filepath} not found.")
        return False
    
    try:
        with open(filepath, 'r') as f:
            report = json.load(f)
            
        summary = report.get("summary", {})
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        total = passed + failed
        
        pass_rate = (passed / total * 100) if total > 0 else 0.0
        print("=== PYTEST E2E RESULTS ANALYSIS ===")
        print(f"Total Tests: {total} | Passed: {passed} | Failed: {failed}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        # Check slow tests (> 10s)
        slow_tests = []
        for test in report.get("tests", []):
            duration = test.get("duration", 0)
            if duration > 10.0:
                slow_tests.append((test.get("nodeid"), duration))
        
        if slow_tests:
            print("\n⚠️ Slow Tests Detected (> 10.0 seconds):")
            for nodeid, dur in slow_tests:
                print(f"  - {nodeid}: {dur:.2f}s")
                
        # List failed test reasons
        if failed > 0:
            print("\n❌ Failed Test Exceptions:")
            for test in report.get("tests", []):
                if test.get("outcome") == "failed":
                    call = test.get("call", {})
                    longrepr = call.get("longrepr", "No traceback info")
                    print(f"\nTest: {test.get('nodeid')}")
                    print(f"Traceback:\n{longrepr}")
                    
        return failed == 0
    except Exception as e:
        print(f"Failed to parse pytest JSON report: {e}")
        return False

def analyze_robot_xml(filepath):
    """
    Parses Robot Framework output.xml to extract E2E metrics.
    """
    if not os.path.exists(filepath):
        print(f"Error: Robot output.xml file {filepath} not found.")
        return False
        
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # Parse status stats
        stats = root.find(".//statistics/total/stat")
        passed = int(stats.attrib.get("pass", 0))
        failed = int(stats.attrib.get("fail", 0))
        total = passed + failed
        pass_rate = (passed / total * 100) if total > 0 else 0.0
        
        print("=== ROBOT FRAMEWORK E2E RESULTS ANALYSIS ===")
        print(f"Total Tests: {total} | Passed: {passed} | Failed: {failed}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        # Check failures
        if failed > 0:
            print("\n❌ Failed Robot Test Cases:")
            for test in root.findall(".//suite//test"):
                status = test.find("status")
                if status is not None and status.attrib.get("status") == "FAIL":
                    name = test.attrib.get("name")
                    message = status.text
                    print(f"  - {name}: {message}")
                    
        return failed == 0
    except Exception as e:
        print(f"Failed to parse Robot output.xml: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze-e2e-results.py <results_file.json|output.xml>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    if filepath.endswith(".json"):
        success = analyze_pytest_json(filepath)
    elif filepath.endswith(".xml"):
        success = analyze_robot_xml(filepath)
    else:
        print("Error: Unsupported file format. Please provide a .json (pytest-json-report) or .xml (robot output.xml) file.")
        sys.exit(1)
        
    sys.exit(0 if success else 1)