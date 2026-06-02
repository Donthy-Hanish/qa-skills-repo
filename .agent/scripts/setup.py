#!/usr/bin/env python3
"""
QA Skills Repository - Dynamic Setup Script

Discovers all skills in .agent/skills/ and reads each skill's
requirements.json to install dependencies.

No hardcoded skill list. Add a new skill with a requirements.json
and this script picks it up automatically.

Usage:
    python scripts/setup.py                              # Install all
    python scripts/setup.py --skill lighthouse-auditor   # Install one
    python scripts/setup.py --check                      # Check status
    python scripts/setup.py --list                       # List all skills and their deps
"""

import subprocess
import sys
import os
import json
import shutil
import argparse
from pathlib import Path


SKILLS_DIR = Path(__file__).parent.parent / ".agent" / "skills"


def find_skills():
    """Discover all skills that have a requirements.json."""
    skills = {}
    if not SKILLS_DIR.exists():
        print(f"  Skills directory not found: {SKILLS_DIR}")
        return skills

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.startswith("."):
            continue

        req_file = skill_dir / "requirements.json"
        if req_file.exists():
            with open(req_file, "r", encoding="utf-8") as f:
                skills[skill_dir.name] = json.load(f)
        else:
            # Skill exists but has no requirements (e.g., test-case-generator)
            skills[skill_dir.name] = {
                "skill": skill_dir.name,
                "python": [],
                "node": [],
                "commands": [],
                "notes": "No requirements.json found. No runtime dependencies."
            }

    return skills


def run_cmd(cmd, description):
    """Run a shell command with status reporting."""
    print(f"\n  Installing: {description}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"  Done.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  FAILED: {e}")
        print(f"  You may need to install this manually.")
        return False


def check_tool(name):
    """Check if a CLI tool is available."""
    found = shutil.which(name) is not None
    symbol = "+" if found else "x"
    status = "FOUND" if found else "MISSING"
    print(f"    [{symbol}] {name:30s} {status}")
    return found


def check_python_pkg(pkg):
    """Check if a Python package is installed."""
    try:
        # Handle robotframework package naming
        import_name = pkg.replace("-", "_")
        if import_name.startswith("robotframework_"):
            # robotframework-seleniumlibrary -> SeleniumLibrary
            import_name = "robot"
        __import__(import_name)
        print(f"    [+] {pkg:30s} FOUND")
        return True
    except ImportError:
        # Try pip show as fallback
        result = subprocess.run(
            f"pip show {pkg}",
            shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"    [+] {pkg:30s} FOUND")
            return True
        print(f"    [x] {pkg:30s} MISSING")
        return False


def check_node_pkg(pkg):
    """Check if a Node package is available."""
    # Check global npm packages
    result = subprocess.run(
        f"npm list -g {pkg} --depth=0",
        shell=True, capture_output=True, text=True
    )
    if result.returncode == 0 and pkg in result.stdout:
        print(f"    [+] {pkg:30s} FOUND")
        return True
    print(f"    [x] {pkg:30s} MISSING")
    return False


def check_all():
    """Check all dependencies for all skills."""
    print("\n" + "=" * 55)
    print("  Dependency Check - QA Skills Repository")
    print("=" * 55)

    # System tools
    print("\n  System Tools:")
    all_ok = True
    for tool in ["python", "pip", "node", "npm", "npx", "git"]:
        all_ok &= check_tool(tool)

    # Per-skill check
    skills = find_skills()
    for name, deps in skills.items():
        print(f"\n  Skill: {name}")

        if deps.get("python"):
            print("    Python packages:")
            for pkg in deps["python"]:
                all_ok &= check_python_pkg(pkg)

        if deps.get("node"):
            print("    Node packages:")
            for pkg in deps["node"]:
                all_ok &= check_node_pkg(pkg)

        if deps.get("system"):
            print("    System dependencies:")
            for dep in deps["system"]:
                print(f"    [?] {dep}  (check manually)")

        if not deps.get("python") and not deps.get("node"):
            print("    No runtime dependencies.")

    print("\n" + "=" * 55)
    if all_ok:
        print("  All dependencies installed!")
    else:
        print("  Some dependencies are missing.")
        print("  Run: python scripts/setup.py")
    print("=" * 55 + "\n")
    return all_ok


def install_skill(skill_name):
    """Install dependencies for one skill."""
    skills = find_skills()
    if skill_name not in skills:
        print(f"\n  Skill '{skill_name}' not found.")
        print(f"  Available: {', '.join(skills.keys())}")
        return

    deps = skills[skill_name]
    print(f"\n  Setting up: {skill_name}")

    if deps.get("python"):
        pkgs = " ".join(deps["python"])
        run_cmd(f"pip install {pkgs}", f"Python: {pkgs}")

    if deps.get("node"):
        pkgs = " ".join(deps["node"])
        run_cmd(f"npm install -g {pkgs}", f"Node: {pkgs}")

    for cmd in deps.get("commands", []):
        run_cmd(cmd, cmd)

    if deps.get("system"):
        print("\n  Manual installation needed:")
        for dep in deps["system"]:
            print(f"    - {dep}")

    if deps.get("notes"):
        print(f"\n  Note: {deps['notes']}")

    print(f"\n  {skill_name} setup complete.")


def install_all():
    """Install dependencies for all skills."""
    skills = find_skills()
    if not skills:
        print("  No skills found.")
        return

    print(f"\n  Found {len(skills)} skills. Installing all dependencies...")

    # Collect and deduplicate
    all_python = set()
    all_node = set()
    all_commands = set()
    all_system = []

    for deps in skills.values():
        all_python.update(deps.get("python", []))
        all_node.update(deps.get("node", []))
        all_commands.update(deps.get("commands", []))
        all_system.extend(deps.get("system", []))

    if all_python:
        pkgs = " ".join(sorted(all_python))
        run_cmd(f"pip install {pkgs}", f"Python packages ({len(all_python)})")

    if all_node:
        pkgs = " ".join(sorted(all_node))
        run_cmd(f"npm install -g {pkgs}", f"Node packages ({len(all_node)})")

    for cmd in sorted(all_commands):
        run_cmd(cmd, cmd)

    if all_system:
        print("\n  Manual installation needed:")
        for dep in set(all_system):
            print(f"    - {dep}")

    print(f"\n  All done. Run 'python scripts/setup.py --check' to verify.")


def list_skills():
    """List all skills and their dependencies."""
    skills = find_skills()
    print(f"\n  {'Skill':<30s} {'Python':<6s} {'Node':<6s} {'Cmds':<6s}")
    print("  " + "-" * 50)
    for name, deps in skills.items():
        py = len(deps.get("python", []))
        nd = len(deps.get("node", []))
        cm = len(deps.get("commands", []))
        print(f"  {name:<30s} {py:<6d} {nd:<6d} {cm:<6d}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QA Skills Setup")
    parser.add_argument("--skill", help="Install for a specific skill")
    parser.add_argument("--check", action="store_true", help="Check deps")
    parser.add_argument("--list", action="store_true", help="List skills")
    args = parser.parse_args()

    if args.check:
        check_all()
    elif args.list:
        list_skills()
    elif args.skill:
        install_skill(args.skill)
    else:
        install_all()
