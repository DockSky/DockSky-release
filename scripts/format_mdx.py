#!/usr/bin/env python3
"""Normalize DockSky Docusaurus MDX formatting.

Fixes common authoring glitches:
- headings/lists/tables/blockquotes glued after a colon on the same line
- numbered list items chained on one line
- triple spaces used as pseudo line breaks

Usage:
  python3 scripts/format_mdx.py          # format docs/**/*.mdx in place
  python3 scripts/format_mdx.py --check # exit 1 if changes would be needed
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

HEADING_GLUE = re.compile(r":\s+(#{1,6}\s)")
BLOCKQUOTE_GLUE = re.compile(r":\s+(>)")
TABLE_GLUE = re.compile(r":\s+(\|)")
LIST_GLUE = re.compile(r":\s+(-\s)")
ORDERED_START_GLUE = re.compile(r":\s+(1\.\s)")
ORDERED_CONTINUE_GLUE = re.compile(r"(\S)\s+(\d+)\.\s+(\*\*)")
TRIPLE_SPACE = re.compile(r"   +")


def format_line(line: str) -> str:
    if line.strip().startswith("```"):
        return line

    line = HEADING_GLUE.sub(r":\n\n\1", line)
    line = BLOCKQUOTE_GLUE.sub(r":\n\n\1", line)
    line = TABLE_GLUE.sub(r":\n\n\1", line)
    line = LIST_GLUE.sub(r":\n\n\1", line)
    line = ORDERED_START_GLUE.sub(r":\n\n\1", line)
    line = ORDERED_CONTINUE_GLUE.sub(r"\1\n\n\2. \3", line)
    line = TRIPLE_SPACE.sub(" — ", line)
    return line


def format_content(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_fence = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        expanded = format_line(line).split("\n")
        out.extend(expanded)

    result = "\n".join(out)
    if text.endswith("\n"):
        result += "\n"
    return result


def scan_issues(text: str, rel: str) -> list[str]:
    issues: list[str] = []
    in_fence = False
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if HEADING_GLUE.search(line):
            issues.append(f"{rel}:{i}: glued heading")
        if BLOCKQUOTE_GLUE.search(line):
            issues.append(f"{rel}:{i}: glued blockquote")
        if TABLE_GLUE.search(line):
            issues.append(f"{rel}:{i}: glued table")
        if LIST_GLUE.search(line):
            issues.append(f"{rel}:{i}: glued list")
        if ORDERED_START_GLUE.search(line):
            issues.append(f"{rel}:{i}: glued ordered list")
        if ORDERED_CONTINUE_GLUE.search(line):
            issues.append(f"{rel}:{i}: chained ordered list")
        if TRIPLE_SPACE.search(line):
            issues.append(f"{rel}:{i}: triple space")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write files; exit 1 if formatting is needed",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional MDX files (default: all under docs/)",
    )
    args = parser.parse_args()

    files = (
        sorted(args.paths)
        if args.paths
        else sorted(DOCS_DIR.rglob("*.mdx"))
    )

    changed = 0
    remaining: list[str] = []

    for path in files:
        original = path.read_text(encoding="utf-8")
        formatted = format_content(original)
        rel = str(path.relative_to(DOCS_DIR.parent))

        if formatted != original:
            changed += 1
            if args.check:
                print(f"would reformat {rel}")
            else:
                path.write_text(formatted, encoding="utf-8")
                print(f"formatted {rel}")

        remaining.extend(scan_issues(formatted, rel))

    if remaining:
        print("\nRemaining issues after format:", file=sys.stderr)
        for issue in remaining:
            print(f"  {issue}", file=sys.stderr)
        return 1

    if args.check and changed:
        print(f"{changed} file(s) need formatting", file=sys.stderr)
        return 1

    if not args.check:
        print(f"Done — {changed} file(s) updated, 0 issues remaining")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
