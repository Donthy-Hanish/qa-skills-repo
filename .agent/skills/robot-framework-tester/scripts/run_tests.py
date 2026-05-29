#!/usr/bin/env python3
"""
run_tests.py - Helper script to run Robot Framework test suites.

Supports:
- Running the full suite
- Running by tags (include/exclude)
- Parallel execution using pabot
- Custom output directory and browser options
"""

import argparse
import os
import subprocess
import sys


def run_command(cmd):
    """Executes a shell command and streams output to console."""
    print(f"\n[EXEC] Running: {' '.join(cmd)}")
    try:
        # Run subprocess and stream output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                sys.stdout.write(output)
                sys.stdout.flush()
                
        rc = process.poll()
        return rc
    except FileNotFoundError as e:
        print(f"\n[ERROR] Command not found: {e.filename}. Is it installed in your PATH?")
        return 127
    except Exception as e:
        print(f"\n[ERROR] Failed to run command: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Helper utility for running Robot Framework and Pabot test suites.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                          # Run all tests in 'tests' directory
  python run_tests.py --tag smoke              # Run tests tagged with 'smoke'
  python run_tests.py --tag smoke,regression   # Run tests with 'smoke' OR 'regression'
  python run_tests.py --exclude wip            # Exclude tests tagged with 'wip'
  python run_tests.py --pabot --processes 4    # Run in parallel using 4 processes
  python run_tests.py --outputdir custom_out   # Save execution artifacts in custom_out/
"""
    )
    
    parser.add_argument(
        "--tests", "-d",
        default="tests",
        help="Path to tests directory or specific .robot file (default: tests)"
    )
    parser.add_argument(
        "--tag", "-t",
        help="Run tests matching these tags (comma-separated for multiple tags)"
    )
    parser.add_argument(
        "--exclude", "-e",
        help="Exclude tests matching these tags (comma-separated)"
    )
    parser.add_argument(
        "--pabot",
        action="store_true",
        help="Use pabot for parallel test execution"
    )
    parser.add_argument(
        "--processes", "-p",
        type=int,
        default=4,
        help="Number of parallel processes to use with pabot (default: 4)"
    )
    parser.add_argument(
        "--outputdir", "-o",
        default="results",
        help="Directory where output files (log, report, xml) will be saved (default: results)"
    )
    parser.add_argument(
        "--variable", "-v",
        action="append",
        help="Pass individual variables to Robot (e.g. -v BROWSER:headlesschrome)"
    )
    parser.add_argument(
        "--variablefile", "-V",
        action="append",
        help="Path to variable file (e.g. -V config/dev.yaml)"
    )
    
    args, unknown = parser.parse_known_args()
    
    # Base command: pabot or robot
    if args.pabot:
        cmd = ["pabot", "--processes", str(args.processes)]
    else:
        cmd = ["robot"]
        
    # Add output directory
    cmd.extend(["--outputdir", args.outputdir])
    
    # Process included tags
    if args.tag:
        # robot allows running multiple tags separated by OR/AND or multiple --include args
        # We split by comma and include each one
        for t in args.tag.split(","):
            cmd.extend(["--include", t.strip()])
            
    # Process excluded tags
    if args.exclude:
        for ex in args.exclude.split(","):
            cmd.extend(["--exclude", ex.strip()])
            
    # Process variables
    if args.variable:
        for var in args.variable:
            cmd.extend(["--variable", var])
            
    # Process variable files
    if args.variablefile:
        for vf in args.variablefile:
            cmd.extend(["--variablefile", vf])
            
    # Forward any unknown arguments directly to robot/pabot
    if unknown:
        cmd.extend(unknown)
        
    # Append the target tests directory/file
    cmd.append(args.tests)
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.outputdir):
        os.makedirs(args.outputdir, exist_ok=True)
        
    rc = run_command(cmd)
    
    print("\n" + "=" * 40)
    if rc == 0:
        print("[SUCCESS] All tests passed!")
    elif rc == 250:
        print("[WARNING] Critical tests failed, but suite ran to completion.")
    else:
        print(f"[FAILURE] Test execution failed with exit code: {rc}")
    print(f"Artifacts saved to: {os.path.abspath(args.outputdir)}")
    print("=" * 40 + "\n")
    
    sys.exit(rc)


if __name__ == "__main__":
    main()
