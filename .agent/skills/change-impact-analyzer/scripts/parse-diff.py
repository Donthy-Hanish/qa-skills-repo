#!/usr/bin/env python3
"""
parse-diff.py - Parse a unified diff and extract structured change data.

Usage:
    python parse-diff.py <diff-file>
    python parse-diff.py --stdin  (read diff from stdin)

Output: JSON to stdout with changed files, functions, and line ranges.
"""

import sys
import re
import json
import argparse
from pathlib import Path


def parse_unified_diff(diff_text: str) -> list[dict]:
    """Parse a unified diff into structured change records."""
    files = []
    current_file = None
    current_hunks = []

    for line in diff_text.splitlines():
        # Detect file header: --- a/path or +++ b/path
        if line.startswith("--- a/") or line.startswith("--- /dev/null"):
            # Save previous file if any
            if current_file:
                current_file["hunks"] = current_hunks
                files.append(current_file)
            old_path = line[6:] if line.startswith("--- a/") else "/dev/null"
            current_file = {
                "old_path": old_path,
                "new_path": None,
                "status": "modified",
                "hunks": [],
                "functions_changed": [],
                "lines_added": 0,
                "lines_removed": 0,
            }
            current_hunks = []
            continue

        if line.startswith("+++ b/") or line.startswith("+++ /dev/null"):
            if current_file:
                new_path = line[6:] if line.startswith("+++ b/") else "/dev/null"
                current_file["new_path"] = new_path
                # Classify status
                if current_file["old_path"] == "/dev/null":
                    current_file["status"] = "added"
                elif new_path == "/dev/null":
                    current_file["status"] = "deleted"
            continue

        # Detect hunk header: @@ -old_start,old_count +new_start,new_count @@ optional_context
        hunk_match = re.match(
            r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\s*(.*)", line
        )
        if hunk_match:
            context = hunk_match.group(5).strip()
            hunk = {
                "old_start": int(hunk_match.group(1)),
                "old_count": int(hunk_match.group(2) or 1),
                "new_start": int(hunk_match.group(3)),
                "new_count": int(hunk_match.group(4) or 1),
                "context": context,
            }
            current_hunks.append(hunk)
            # The context line often contains the function/class name
            if context and current_file:
                current_file["functions_changed"].append(context)
            continue

        # Count additions and removals
        if current_file:
            if line.startswith("+") and not line.startswith("+++"):
                current_file["lines_added"] += 1
            elif line.startswith("-") and not line.startswith("---"):
                current_file["lines_removed"] += 1

    # Save last file
    if current_file:
        current_file["hunks"] = current_hunks
        files.append(current_file)

    return files


def classify_file(filepath: str) -> str:
    """Classify a file by its layer based on path and extension."""
    if not filepath or filepath == "/dev/null":
        return "unknown"

    fp = filepath.lower()
    ext = Path(filepath).suffix.lower()

    # Migration files
    if "migration" in fp or "alembic" in fp or "flyway" in fp:
        return "migration"

    # Config files
    if ext in (".env", ".yaml", ".yml", ".toml", ".ini", ".cfg"):
        return "config"
    if any(name in fp for name in ("config", ".env", "settings")):
        return "config"

    # Test files
    if "test" in fp or "spec" in fp or "__tests__" in fp:
        return "test"

    # Infrastructure
    if any(name in fp for name in ("docker", "terraform", "cloudformation", "k8s", "helm", "infra")):
        return "infrastructure"

    # UI layer
    if ext in (".tsx", ".jsx", ".vue", ".svelte", ".html", ".css", ".scss"):
        return "ui"
    if any(name in fp for name in ("components/", "pages/", "views/", "frontend/")):
        return "ui"

    # API layer
    if any(name in fp for name in ("controller", "route", "endpoint", "handler", "api/")):
        return "api"

    # Service layer
    if any(name in fp for name in ("service", "usecase", "interactor")):
        return "service"

    # Repository / data layer
    if any(name in fp for name in ("repo", "repository", "model", "schema", "entity", "dao")):
        return "repository"

    # SQL files
    if ext == ".sql":
        return "migration"

    return "source"


def summarize(files: list[dict]) -> dict:
    """Produce a summary of the parsed diff."""
    total_added = sum(f["lines_added"] for f in files)
    total_removed = sum(f["lines_removed"] for f in files)

    layers = {}
    for f in files:
        path = f.get("new_path") or f.get("old_path") or ""
        layer = classify_file(path)
        f["layer"] = layer
        if layer not in layers:
            layers[layer] = []
        layers[layer].append(path)

    return {
        "total_files_changed": len(files),
        "total_lines_added": total_added,
        "total_lines_removed": total_removed,
        "layers_affected": layers,
        "files": files,
    }


def main():
    parser = argparse.ArgumentParser(description="Parse a unified diff into structured JSON")
    parser.add_argument("diff_file", nargs="?", help="Path to diff file")
    parser.add_argument("--stdin", action="store_true", help="Read diff from stdin")
    args = parser.parse_args()

    if args.stdin:
        diff_text = sys.stdin.read()
    elif args.diff_file:
        diff_path = Path(args.diff_file)
        if not diff_path.exists():
            print(f"Error: File not found: {args.diff_file}", file=sys.stderr)
            sys.exit(1)
        diff_text = diff_path.read_text(encoding="utf-8")
    else:
        parser.print_help()
        sys.exit(1)

    files = parse_unified_diff(diff_text)
    result = summarize(files)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
