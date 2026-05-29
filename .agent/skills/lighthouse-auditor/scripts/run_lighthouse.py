#!/usr/bin/env python3
"""
Lighthouse Audit Runner and Parser Utility.
Provides functions to run single or batch URL audits via the Lighthouse CLI,
validate scores and Core Web Vitals against thresholds, and compare two audit runs.
"""

import os
import sys
import json
import subprocess
import argparse
import urllib.parse
from datetime import datetime

# Default thresholds
DEFAULT_THRESHOLDS = {
    "performance": 80.0,
    "accessibility": 90.0,
    "best-practices": 90.0,
    "seo": 90.0,
    "lcp": 2500.0,         # Largest Contentful Paint (ms) - Good: <= 2500ms
    "cls": 0.1,            # Cumulative Layout Shift - Good: <= 0.1
    "tbt": 300.0,          # Total Blocking Time (ms) - Good: <= 300ms
    "speed-index": 3400.0, # Speed Index (ms) - Good: <= 3400ms
    "fid": 100.0,          # First Input Delay (ms) - Good: <= 100ms
    "inp": 200.0           # Interaction to Next Paint (ms) - Good: <= 200ms
}

def run_lighthouse(url, output_dir="reports", preset="desktop", config_path=None, headless=True):
    """
    Runs a Lighthouse audit for a single URL using the command line tool.
    Returns the paths to the generated JSON and HTML files.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse URL to create a safe filename
    parsed_url = urllib.parse.urlparse(url)
    safe_host = parsed_url.netloc.replace(":", "_")
    safe_path = parsed_url.path.strip("/").replace("/", "_")
    name_part = f"{safe_host}_{safe_path}" if safe_path else safe_host
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    base_filename = f"lighthouse_{name_part}_{timestamp}"
    json_path = os.path.join(output_dir, f"{base_filename}.report.json")
    html_path = os.path.join(output_dir, f"{base_filename}.report.html")
    
    # Base command structure
    cmd = [
        "npx", "lighthouse",
        url,
        "--output=json",
        "--output=html",
        f"--output-path={os.path.join(output_dir, base_filename)}"
    ]
    
    # Throttling and headless options
    chrome_flags = ["--headless"] if headless else []
    chrome_flags.append("--no-sandbox")
    chrome_flags.append("--disable-gpu")
    
    cmd.append(f'--chrome-flags="{" ".join(chrome_flags)}"')
    
    if preset == "desktop":
        cmd.append("--preset=desktop")
    elif preset == "mobile":
        # Mobile is default in Lighthouse
        pass
        
    if config_path:
        cmd.extend(["--config-path", config_path])
        
    print(f"Running Lighthouse audit for {url} ({preset} mode)...")
    print(f"Command: {' '.join(cmd)}")
    
    # Run CLI using subprocess
    # On Windows, npx requires shell=True to be found reliably if not using absolute path
    is_windows = os.name == "nt"
    try:
        result = subprocess.run(
            cmd,
            shell=is_windows,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Lighthouse audit completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running Lighthouse CLI:\n{e.stderr}", file=sys.stderr)
        raise e

    # Lighthouse creates <output-path>.report.json and <output-path>.report.html
    # We rename or check if they exist at the correct output path
    # If the output-path contains output extensions, Lighthouse might write there directly
    actual_json_path = os.path.join(output_dir, f"{base_filename}.report.json")
    actual_html_path = os.path.join(output_dir, f"{base_filename}.report.html")
    
    # If Lighthouse named files without .report suffix (depends on LH version)
    if not os.path.exists(actual_json_path):
        alt_json = os.path.join(output_dir, f"{base_filename}.json")
        if os.path.exists(alt_json):
            os.rename(alt_json, actual_json_path)
            
    if not os.path.exists(actual_html_path):
        alt_html = os.path.join(output_dir, f"{base_filename}.html")
        if os.path.exists(alt_html):
            os.rename(alt_html, actual_html_path)
            
    return actual_json_path, actual_html_path

def parse_report(json_path):
    """
    Parses a Lighthouse JSON report and extracts scores and key Core Web Vitals.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Extract Category Scores (multiplied by 100 for 0-100 scale)
    categories = data.get("categories", {})
    scores = {}
    for cat_id in ["performance", "accessibility", "best-practices", "seo"]:
        cat = categories.get(cat_id, {})
        scores[cat_id] = cat.get("score", 0.0) * 100.0 if cat.get("score") is not None else 0.0

    # Extract Audits (Core Web Vitals)
    audits = data.get("audits", {})
    
    def get_numeric(audit_name):
        audit = audits.get(audit_name, {})
        return audit.get("numericValue")

    vitals = {
        "lcp": get_numeric("largest-contentful-paint"),
        "cls": get_numeric("cumulative-layout-shift"),
        "tbt": get_numeric("total-blocking-time"),
        "speed-index": get_numeric("speed-index"),
        "fid": get_numeric("max-potential-fid"),
        "inp": get_numeric("interaction-to-next-paint")
    }
    
    return {
        "url": data.get("requestedUrl"),
        "fetchTime": data.get("fetchTime"),
        "scores": scores,
        "vitals": vitals
    }

def assert_thresholds(metrics, thresholds=None):
    """
    Asserts extracted metrics against thresholds.
    Returns a dictionary of result status and a list of failure messages.
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
        
    failures = []
    
    # Assert Category Scores (min scores)
    scores = metrics["scores"]
    for cat in ["performance", "accessibility", "best-practices", "seo"]:
        target = thresholds.get(cat, DEFAULT_THRESHOLDS[cat])
        actual = scores.get(cat, 0.0)
        if actual < target:
            failures.append(
                f"FAIL: {cat.capitalize()} Score {actual:.1f} is below threshold {target:.1f}"
            )
            
    # Assert Web Vitals (max limits)
    vitals = metrics["vitals"]
    vital_limits = {
        "lcp": ("LCP", "ms", True),         # (Name, Unit, IsLowerBetter)
        "cls": ("CLS", "", True),
        "tbt": ("TBT", "ms", True),
        "speed-index": ("Speed Index", "ms", True),
        "fid": ("FID", "ms", True),
        "inp": ("INP", "ms", True)
    }
    
    for key, (name, unit, lower_better) in vital_limits.items():
        actual = vitals.get(key)
        target = thresholds.get(key)
        
        if actual is None:
            continue
            
        if target is None:
            target = DEFAULT_THRESHOLDS.get(key)
            
        if target is not None:
            if lower_better and actual > target:
                unit_str = f" {unit}" if unit else ""
                failures.append(
                    f"FAIL: {name} is {actual:.2f}{unit_str}, exceeding limit of {target:.2f}{unit_str}"
                )
                
    return {
        "passed": len(failures) == 0,
        "failures": failures
    }

def compare_reports(before_path, after_path):
    """
    Compares two Lighthouse JSON reports and prints/returns the difference.
    """
    before = parse_report(before_path)
    after = parse_report(after_path)
    
    comparison = {
        "urls": {"before": before["url"], "after": after["url"]},
        "times": {"before": before["fetchTime"], "after": after["fetchTime"]},
        "scores": {},
        "vitals": {}
    }
    
    # Compare Category Scores
    for cat in ["performance", "accessibility", "best-practices", "seo"]:
        b_val = before["scores"].get(cat, 0.0)
        a_val = after["scores"].get(cat, 0.0)
        diff = a_val - b_val
        comparison["scores"][cat] = {
            "before": b_val,
            "after": a_val,
            "diff": diff
        }
        
    # Compare Vitals
    for key in ["lcp", "cls", "tbt", "speed-index", "fid", "inp"]:
        b_val = before["vitals"].get(key)
        a_val = after["vitals"].get(key)
        
        if b_val is None or a_val is None:
            diff = None
        else:
            diff = a_val - b_val
            
        comparison["vitals"][key] = {
            "before": b_val,
            "after": a_val,
            "diff": diff
        }
        
    return comparison

def format_comparison_markdown(comp):
    """
    Formats the comparison dict into a beautiful markdown table.
    """
    lines = []
    lines.append("# Lighthouse Audit Comparison Report")
    lines.append("")
    lines.append(f"- **Before URL**: {comp['urls']['before']} (Audited: {comp['times']['before']})")
    lines.append(f"- **After URL**: {comp['urls']['after']} (Audited: {comp['times']['after']})")
    lines.append("")
    lines.append("## Category Scores (Higher is Better)")
    lines.append("| Category | Before | After | Diff | Status |")
    lines.append("|---|---|---|---|---|")
    
    for cat, val in comp["scores"].items():
        diff = val["diff"]
        diff_str = f"+{diff:.1f}" if diff > 0 else f"{diff:.1f}"
        if diff > 0:
            status = "🟢 Improved"
        elif diff < 0:
            status = "🔴 Regressed"
        else:
            status = "⚪ Unchanged"
        lines.append(f"| {cat.capitalize()} | {val['before']:.1f} | {val['after']:.1f} | {diff_str} | {status} |")
        
    lines.append("")
    lines.append("## Core Web Vitals (Lower is Better)")
    lines.append("| Metric | Unit | Before | After | Diff | Status |")
    lines.append("|---|---|---|---|---|---|")
    
    units = {
        "lcp": ("Largest Contentful Paint", "ms"),
        "cls": ("Cumulative Layout Shift", ""),
        "tbt": ("Total Blocking Time", "ms"),
        "speed-index": ("Speed Index", "ms"),
        "fid": ("First Input Delay", "ms"),
        "inp": ("Interaction to Next Paint", "ms")
    }
    
    for key, val in comp["vitals"].items():
        name, unit = units[key]
        b_val = val["before"]
        a_val = val["after"]
        diff = val["diff"]
        
        if b_val is None or a_val is None:
            lines.append(f"| {name} | {unit} | N/A | N/A | N/A | - |")
            continue
            
        diff_str = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
        
        # For vitals, lower is better. Thus positive diff is regression, negative is improvement.
        if diff < 0:
            status = "🟢 Improved"
        elif diff > 0:
            status = "🔴 Regressed"
        else:
            status = "⚪ Unchanged"
            
        b_str = f"{b_val:.2f}" if key == "cls" else f"{b_val:.0f}"
        a_str = f"{a_val:.2f}" if key == "cls" else f"{a_val:.0f}"
        d_str = f"{diff:.2f}" if key == "cls" else f"{diff:.0f}"
        if diff > 0:
            d_str = f"+{d_str}"
            
        lines.append(f"| {name} | {unit} | {b_str} | {a_str} | {d_str} | {status} |")
        
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Lighthouse Audit runner, assertor, and comparator.")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")
    
    # Audit subcommand
    audit_parser = subparsers.add_parser("audit", help="Run a Lighthouse audit on one or more URLs")
    audit_parser.add_argument("--url", help="Single URL to audit")
    audit_parser.add_argument("--urls-file", help="File containing list of URLs to audit (one per line)")
    audit_parser.add_argument("--output-dir", default="reports", help="Directory to save report outputs")
    audit_parser.add_argument("--preset", default="desktop", choices=["mobile", "desktop"], help="Audit preset mode")
    audit_parser.add_argument("--config", help="Path to custom Lighthouse config file")
    audit_parser.add_argument("--thresholds", help="Path to JSON file containing threshold config overrides")
    audit_parser.add_argument("--no-headless", action="store_true", help="Run browser in non-headless mode")
    
    # Compare subcommand
    compare_parser = subparsers.add_parser("compare", help="Compare two Lighthouse JSON reports")
    compare_parser.add_argument("before", help="Path to the 'before' Lighthouse JSON report")
    compare_parser.add_argument("after", help="Path to the 'after' Lighthouse JSON report")
    compare_parser.add_argument("--output-md", help="Path to write the comparison Markdown output")
    
    args = parser.parse_args()
    
    if args.command == "audit":
        urls = []
        if args.url:
            urls.append(args.url)
        elif args.urls_file:
            if not os.path.exists(args.urls_file):
                print(f"Error: URLs file not found at {args.urls_file}", file=sys.stderr)
                sys.exit(1)
            with open(args.urls_file, "r") as f:
                urls = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        else:
            audit_parser.print_help()
            sys.exit(1)
            
        # Parse Thresholds override if provided
        thresholds = DEFAULT_THRESHOLDS.copy()
        if args.thresholds:
            if not os.path.exists(args.thresholds):
                print(f"Error: Thresholds file not found at {args.thresholds}", file=sys.stderr)
                sys.exit(1)
            with open(args.thresholds, "r") as f:
                thresholds.update(json.load(f))
                
        all_passed = True
        for url in urls:
            try:
                json_path, html_path = run_lighthouse(
                    url=url,
                    output_dir=args.output_dir,
                    preset=args.preset,
                    config_path=args.config,
                    headless=not args.no_headless
                )
                
                # Parse metrics
                metrics = parse_report(json_path)
                
                # Print results
                print("\n" + "=" * 50)
                print(f"Audit Results for: {metrics['url']}")
                print("-" * 50)
                print(f"Performance Score:      {metrics['scores']['performance']:.1f}")
                print(f"Accessibility Score:    {metrics['scores']['accessibility']:.1f}")
                print(f"Best Practices Score:   {metrics['scores']['best-practices']:.1f}")
                print(f"SEO Score:              {metrics['scores']['seo']:.1f}")
                print("-" * 50)
                print("Core Web Vitals:")
                for k, v in metrics["vitals"].items():
                    val_str = f"{v:.2f}" if k == "cls" else (f"{v:.0f} ms" if v is not None else "N/A")
                    print(f"  {k.upper()}: {val_str}")
                print("=" * 50)
                
                # Assert thresholds
                result = assert_thresholds(metrics, thresholds)
                if not result["passed"]:
                    print("\nThreshold Failures:")
                    for fail in result["failures"]:
                        print(f"  * {fail}")
                    all_passed = False
                else:
                    print("\nAll threshold assertions PASSED.")
                    
            except Exception as e:
                print(f"Failed to audit URL {url}: {e}", file=sys.stderr)
                all_passed = False
                
        if not all_passed:
            sys.exit(1)
            
    elif args.command == "compare":
        if not os.path.exists(args.before) or not os.path.exists(args.after):
            print("Error: Make sure both 'before' and 'after' JSON files exist.", file=sys.stderr)
            sys.exit(1)
            
        comp = compare_reports(args.before, args.after)
        md_content = format_comparison_markdown(comp)
        
        print("\n" + md_content + "\n")
        
        if args.output_md:
            with open(args.output_md, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"Comparison report saved to {args.output_md}")
            
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
