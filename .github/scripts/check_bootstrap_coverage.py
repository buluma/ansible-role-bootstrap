#!/usr/bin/env python3
"""Check that special-case bootstrap package keys are represented in CI coverage metadata."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VARS_FILE = ROOT / "vars" / "main.yml"
WORKFLOW_FILE = ROOT / ".github" / "workflows" / "molecule.yml"

# Keys with version-specific logic that should stay visible in CI metadata.
REQUIRED_SPECIAL_KEYS = {
    "AlmaLinux_8",
    "CentOS_8",
    "Debian_10",
    "Debian_11",
    "Debian_12",
    "OracleLinux_8",
    "RedHat_8",
    "Rocky_8",
}


def parse_bootstrap_package_keys(text: str) -> set[str]:
    in_packages = False
    keys: set[str] = set()
    for line in text.splitlines():
        if line.startswith("_bootstrap_packages:"):
            in_packages = True
            continue
        if in_packages and re.match(r"^[A-Za-z_].*:$", line):
            break
        if in_packages:
            match = re.match(r'^\s{2}"?([^":]+)"?:\s+', line)
            if match:
                keys.add(match.group(1))
    return keys


def parse_coverage_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for line in text.splitlines():
        match = re.search(r'covers:\s*"([^"]+)"', line)
        if not match:
            continue
        for key in match.group(1).split(","):
            stripped = key.strip()
            if stripped:
                keys.add(stripped)
    return keys


def main() -> int:
    vars_text = VARS_FILE.read_text(encoding="utf-8")
    workflow_text = WORKFLOW_FILE.read_text(encoding="utf-8")

    vars_keys = parse_bootstrap_package_keys(vars_text)
    coverage_keys = parse_coverage_keys(workflow_text)

    missing_from_vars = sorted(REQUIRED_SPECIAL_KEYS - vars_keys)
    missing_from_workflow = sorted(REQUIRED_SPECIAL_KEYS - coverage_keys)

    problems: list[str] = []
    if missing_from_vars:
        problems.append(
            "required keys not found in vars/main.yml: " + ", ".join(missing_from_vars)
        )
    if missing_from_workflow:
        problems.append(
            "required keys missing from molecule matrix coverage metadata: "
            + ", ".join(missing_from_workflow)
        )

    strict = os.getenv("BOOTSTRAP_COVERAGE_STRICT", "true").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    if problems:
        level = "ERROR" if strict else "WARNING"
        for problem in problems:
            print(f"[{level}] {problem}")
        if strict:
            return 1
    else:
        print(
            "[OK] Bootstrap coverage metadata includes all required special-case keys."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
